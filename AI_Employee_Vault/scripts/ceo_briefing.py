#!/usr/bin/env python3
"""
Weekly CEO Briefing Generator

Generates a comprehensive Monday Morning CEO Briefing by:
1. Analyzing accounting data from Odoo
2. Reviewing completed tasks from Done/ folder
3. Checking social media engagement
4. Identifying bottlenecks and proactive suggestions
"""

import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger('ceo_briefing')

class CEOBriefingGenerator:
    """Generates weekly CEO briefing with business intelligence"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.briefings_path = vault_path / 'Briefings'
        self.done_path = vault_path / 'Done'
        self.business_goals_path = vault_path / 'Business_Goals.md'
        
        # MCP server URLs
        self.odoo_mcp_url = 'http://localhost:8810'
        self.facebook_mcp_url = 'http://localhost:8811'
        
        # Ensure briefings folder exists
        self.briefings_path.mkdir(exist_ok=True)
    
    def _call_mcp(self, url: str, tool: str, params: Dict = None) -> Dict:
        """Call an MCP server tool"""
        try:
            response = requests.post(url, json={
                'tool': tool,
                'params': params or {}
            }, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'MCP call failed ({tool}): {e}')
            return {'success': False, 'error': str(e)}
    
    def get_financial_data(self, date_from: str, date_to: str) -> Dict:
        """Get financial summary from Odoo"""
        logger.info('📊 Fetching financial data from Odoo...')
        
        result = self._call_mcp(
            self.odoo_mcp_url,
            'odoo_get_financial_summary',
            {'date_from': date_from, 'date_to': date_to}
        )
        
        if result.get('success'):
            logger.info(f'   Revenue: ${result.get("total_invoiced", 0):.2f}')
            logger.info(f'   Paid: ${result.get("total_paid", 0):.2f}')
            logger.info(f'   Outstanding: ${result.get("total_outstanding", 0):.2f}')
        
        return result
    
    def get_completed_tasks(self, date_from: datetime) -> List[Path]:
        """Get tasks completed since date_from"""
        logger.info('📋 Analyzing completed tasks...')
        
        if not self.done_path.exists():
            logger.warning('   Done/ folder not found')
            return []
        
        completed = []
        for file_path in self.done_path.glob('*.md'):
            # Check file modification time
            if datetime.fromtimestamp(file_path.stat().st_mtime) >= date_from:
                completed.append(file_path)
        
        logger.info(f'   Found {len(completed)} completed tasks')
        return completed
    
    def get_social_media_summary(self, date_from: str, date_to: str) -> Dict:
        """Get social media summaries from Facebook/Instagram"""
        logger.info('📱 Fetching social media data...')
        
        facebook_summary = self._call_mcp(
            self.facebook_mcp_url,
            'facebook_get_summary',
            {'date_from': date_from, 'date_to': date_to}
        )
        
        return {
            'facebook': facebook_summary
        }
    
    def analyze_bottlenecks(self, completed_tasks: List[Path]) -> List[Dict]:
        """Identify bottlenecks from task completion times"""
        logger.info('🔍 Analyzing bottlenecks...')
        
        bottlenecks = []
        
        # Look for tasks that took multiple iterations (from Ralph state files)
        state_file = Path('/tmp/ralph_state.json')
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                if state.get('iterations_used', 0) > 5:
                    bottlenecks.append({
                        'type': 'high_iterations',
                        'description': f'Task required {state["iterations_used"]} iterations',
                        'severity': 'warning'
                    })
            except:
                pass
        
        # Check for rejected tasks
        rejected_path = self.vault_path / 'Rejected'
        if rejected_path.exists():
            rejected = list(rejected_path.glob('*.md'))
            if rejected:
                bottlenecks.append({
                    'type': 'rejected_tasks',
                    'description': f'{len(rejected)} tasks rejected by human',
                    'severity': 'info'
                })
        
        logger.info(f'   Found {len(bottlenecks)} potential bottlenecks')
        return bottlenecks
    
    def generate_proactive_suggestions(self, financial_data: Dict, 
                                      completed_tasks: List[Path]) -> List[Dict]:
        """Generate proactive suggestions based on data analysis"""
        logger.info('💡 Generating proactive suggestions...')
        
        suggestions = []
        
        # Check outstanding invoices
        outstanding = financial_data.get('total_outstanding', 0)
        if outstanding > 0:
            suggestions.append({
                'type': 'action',
                'category': 'follow_up',
                'title': 'Follow up on outstanding invoices',
                'description': f'${outstanding:.2f} in invoices not yet paid',
                'priority': 'high'
            })
        
        # Check task completion rate
        if len(completed_tasks) < 5:
            suggestions.append({
                'type': 'observation',
                'category': 'productivity',
                'title': 'Low task completion rate',
                'description': 'Only a few tasks completed this week. Review workload.',
                'priority': 'medium'
            })
        
        # Check for recurring subscriptions (would need transaction analysis)
        # This is a placeholder for more sophisticated analysis
        
        logger.info(f'   Generated {len(suggestions)} suggestions')
        return suggestions
    
    def calculate_revenue_trend(self, current_week: Dict) -> str:
        """Calculate revenue trend (on track, ahead, behind)"""
        # Load business goals
        if not self.business_goals_path.exists():
            return 'unknown'
        
        content = self.business_goals_path.read_text()
        
        # Simple parsing - look for monthly goal
        import re
        match = re.search(r'Monthly goal: \$([\d,]+)', content)
        if not match:
            return 'unknown'
        
        monthly_goal = float(match.group(1).replace(',', ''))
        weekly_goal = monthly_goal / 4
        
        current_revenue = current_week.get('total_invoiced', 0)
        
        if current_revenue >= weekly_goal * 1.1:
            return 'ahead'
        elif current_revenue >= weekly_goal * 0.9:
            return 'on track'
        else:
            return 'behind'
    
    def generate_briefing(self, date_from: datetime = None, 
                         date_to: datetime = None) -> Path:
        """Generate the complete CEO briefing"""
        
        # Default to last 7 days
        if not date_from:
            date_from = datetime.now() - timedelta(days=7)
        if not date_to:
            date_to = datetime.now()
        
        date_from_str = date_from.strftime('%Y-%m-%d')
        date_to_str = date_to.strftime('%Y-%m-%d')
        
        logger.info(f'\n{"="*60}')
        logger.info(f'📈 Generating CEO Briefing')
        logger.info(f'   Period: {date_from_str} to {date_to_str}')
        logger.info(f'{"="*60}\n')
        
        # Collect data
        financial_data = self.get_financial_data(date_from_str, date_to_str)
        completed_tasks = self.get_completed_tasks(date_from)
        social_media = self.get_social_media_summary(date_from_str, date_to_str)
        bottlenecks = self.analyze_bottlenecks(completed_tasks)
        suggestions = self.generate_proactive_suggestions(financial_data, completed_tasks)
        
        # Calculate metrics
        revenue_trend = self.calculate_revenue_trend(financial_data)
        
        # Generate briefing document
        briefing = self._format_briefing(
            financial_data=financial_data,
            completed_tasks=completed_tasks,
            social_media=social_media,
            bottlenecks=bottlenecks,
            suggestions=suggestions,
            revenue_trend=revenue_trend,
            period={'from': date_from_str, 'to': date_to_str}
        )
        
        # Save briefing
        briefing_date = datetime.now().strftime('%Y-%m-%d')
        briefing_file = self.briefings_path / f'{briefing_date}_Monday_Briefing.md'
        briefing_file.write_text(briefing)
        
        logger.info(f'\n✅ Briefing saved to: {briefing_file}')
        
        return briefing_file
    
    def _format_briefing(self, financial_data: Dict, completed_tasks: List[Path],
                        social_media: Dict, bottlenecks: List[Dict],
                        suggestions: List[Dict], revenue_trend: str,
                        period: Dict) -> str:
        """Format the briefing document"""
        
        total_invoiced = financial_data.get('total_invoiced', 0)
        total_paid = financial_data.get('total_paid', 0)
        total_outstanding = financial_data.get('total_outstanding', 0)
        
        # Format completed tasks
        tasks_list = ''
        for task_file in completed_tasks[:10]:  # Show max 10
            tasks_list += f'- [x] {task_file.stem}\n'
        
        if not completed_tasks:
            tasks_list = '- No tasks completed this period\n'
        
        # Format bottlenecks
        bottlenecks_list = ''
        for bottleneck in bottlenecks:
            severity_icon = '⚠️' if bottleneck['severity'] == 'warning' else 'ℹ️'
            bottlenecks_list += f'- {severity_icon} {bottleneck["description"]}\n'
        
        if not bottlenecks:
            bottlenecks_list = '- No bottlenecks identified ✅\n'
        
        # Format suggestions
        suggestions_list = ''
        for suggestion in suggestions:
            priority_marker = '🔴' if suggestion['priority'] == 'high' else '🟡'
            suggestions_list += f'- {priority_marker} **{suggestion["title"]}**: {suggestion["description"]}\n'
        
        if not suggestions:
            suggestions_list = '- No proactive suggestions at this time ✅\n'
        
        # Social media metrics
        facebook_data = social_media.get('facebook', {})
        fb_posts = facebook_data.get('posts_count', 0)
        fb_engagement = facebook_data.get('total_engagement', 0)
        
        # Determine trend emoji
        trend_emoji = {'ahead': '📈', 'on track': '✅', 'behind': '📉', 'unknown': '❓'}
        
        briefing = f"""---
generated: {datetime.now().isoformat()}
period: {period['from']} to {period['to']}
generated_by: AI Employee CEO Briefing Generator v1.0
---

# Monday Morning CEO Briefing

## Executive Summary
{trend_emoji.get(revenue_trend, '❓')} Revenue is **{revenue_trend}** this period. {'Strong performance!' if revenue_trend == 'ahead' else 'Keep pushing!' if revenue_trend == 'on track' else 'Need to increase revenue generation.' if revenue_trend == 'behind' else 'Revenue tracking not configured yet.'}

## Revenue

| Metric | Amount |
|--------|--------|
| **This Period** | ${total_invoiced:,.2f} |
| **Collected** | ${total_paid:,.2f} |
| **Outstanding** | ${total_outstanding:,.2f} |
| **Trend** | {revenue_trend.title()} |

## Completed Tasks

{tasks_list}

## Social Media Performance

### Facebook
- Posts: {fb_posts}
- Total Engagement: {fb_engagement}

### Instagram
- Data available via Instagram MCP integration

## Bottlenecks

{bottlenecks_list}

## Proactive Suggestions

{suggestions_list}

## Upcoming Actions

Review pending approvals in `Pending_Approval/` folder.

---

*Generated by AI Employee v1.0 - Gold Tier*
*Next briefing scheduled for next Monday*
"""
        
        return briefing


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Weekly CEO Briefing')
    parser.add_argument('--vault', type=Path, default=Path.cwd(),
                       help='Path to AI Employee Vault')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to analyze (default: 7)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Generate briefing
    generator = CEOBriefingGenerator(args.vault)
    
    date_from = datetime.now() - timedelta(days=args.days)
    briefing_file = generator.generate_briefing(date_from, datetime.now())
    
    logger.info(f'\n📄 Briefing generated: {briefing_file}')
    logger.info(f'   Open in Obsidian to review')


if __name__ == '__main__':
    main()
