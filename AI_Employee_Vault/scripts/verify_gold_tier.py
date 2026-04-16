#!/usr/bin/env python3
"""
Gold Tier Verification Script

Tests all Gold Tier components:
1. Odoo Docker setup
2. Odoo MCP server
3. Facebook MCP server
4. Ralph Wiggum Loop
5. CEO Briefing generator
6. Audit Logger
7. Master Orchestrator
"""

import sys
import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime

class GoldTierVerifier:
    """Verifies all Gold Tier components are operational"""
    
    def __init__(self):
        self.vault_path = Path('AI_Employee_Vault')
        self.results = {}
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, func):
        """Run a test"""
        print(f"\n{'='*60}")
        print(f'🧪 Testing: {name}')
        print(f'{'='*60}')
        
        try:
            result = func()
            if result:
                print(f'✅ PASSED: {name}')
                self.results[name] = 'PASSED'
                self.passed += 1
            else:
                print(f'❌ FAILED: {name}')
                self.results[name] = 'FAILED'
                self.failed += 1
        except Exception as e:
            print(f'❌ FAILED: {name}')
            print(f'   Error: {e}')
            self.results[name] = f'FAILED: {e}'
            self.failed += 1
    
    def test_odoo_docker(self):
        """Test Odoo Docker setup"""
        print('Checking Docker...')
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print('   ⚠️ Docker not installed')
            return False
        
        print('Checking Odoo container...')
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=odoo_community', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )
        
        if 'odoo_community' not in result.stdout:
            print('   ⚠️ Odoo container not running')
            print('   Start with: cd AI_Employee_Vault/odoo && docker-compose up -d')
            return False
        
        print('✅ Odoo container running')
        
        # Check Odoo is accessible
        print('Checking Odoo web interface...')
        try:
            response = requests.get('http://localhost:8069', timeout=5)
            if response.status_code == 200:
                print('✅ Odoo web interface accessible')
                return True
            else:
                print(f'   ⚠️ Odoo returned status {response.status_code}')
                return False
        except requests.exceptions.ConnectionError:
            print('   ⚠️ Cannot connect to Odoo')
            return False
    
    def test_odoo_mcp(self):
        """Test Odoo MCP server"""
        print('Checking Odoo MCP server...')
        
        try:
            response = requests.get('http://localhost:8810/health', timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f'   Status: {health.get("status")}')
                print(f'   Odoo URL: {health.get("odoo_url")}')
                print('✅ Odoo MCP server running')
                return True
            else:
                print(f'   ⚠️ Health check failed: {response.status_code}')
                return False
        except requests.exceptions.ConnectionError:
            print('   ⚠️ Odoo MCP server not running')
            print('   Start with: python .qwen/skills/odoo-mcp/scripts/odoo_mcp_server.py --port 8810')
            return False
    
    def test_facebook_mcp(self):
        """Test Facebook MCP server"""
        print('Checking Facebook MCP server...')
        
        try:
            response = requests.get('http://localhost:8811/health', timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f'   Status: {health.get("status")}')
                print(f'   Page ID: {health.get("page_id")}')
                print('✅ Facebook MCP server running')
                return True
            else:
                print(f'   ⚠️ Health check failed: {response.status_code}')
                return False
        except requests.exceptions.ConnectionError:
            print('   ⚠️ Facebook MCP server not running')
            print('   Start with: python .qwen/skills/facebook-mcp/scripts/facebook_mcp_server.py --port 8811')
            return False
    
    def test_ralph_wiggum(self):
        """Test Ralph Wiggum Loop script exists"""
        print('Checking Ralph Wiggum Loop script...')
        
        script_path = self.vault_path / 'scripts' / 'ralph_wiggum.py'
        if not script_path.exists():
            print('   ❌ Script not found')
            return False
        
        print('✅ Ralph Wiggum script exists')
        
        # Test help
        result = subprocess.run(
            ['python', str(script_path), '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('✅ Ralph Wiggum script executes correctly')
            return True
        else:
            print(f'   ❌ Script execution failed')
            return False
    
    def test_ceo_briefing(self):
        """Test CEO Briefing generator"""
        print('Checking CEO Briefing script...')
        
        script_path = self.vault_path / 'scripts' / 'ceo_briefing.py'
        if not script_path.exists():
            print('   ❌ Script not found')
            return False
        
        print('✅ CEO Briefing script exists')
        
        # Test help
        result = subprocess.run(
            ['python', str(script_path), '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('✅ CEO Briefing script executes correctly')
            return True
        else:
            print(f'   ❌ Script execution failed')
            return False
    
    def test_audit_logger(self):
        """Test Audit Logger"""
        print('Checking Audit Logger...')
        
        script_path = self.vault_path / 'scripts' / 'audit_logger.py'
        if not script_path.exists():
            print('   ❌ Script not found')
            return False
        
        print('✅ Audit Logger script exists')
        
        # Test help
        result = subprocess.run(
            ['python', str(script_path), '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('✅ Audit Logger script executes correctly')
            return True
        else:
            print(f'   ❌ Script execution failed')
            return False
    
    def test_orchestrator(self):
        """Test Master Orchestrator"""
        print('Checking Master Orchestrator...')
        
        script_path = self.vault_path / 'scripts' / 'orchestrator.py'
        if not script_path.exists():
            print('   ❌ Script not found')
            return False
        
        print('✅ Master Orchestrator script exists')
        
        # Test help
        result = subprocess.run(
            ['python', str(script_path), '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('✅ Master Orchestrator script executes correctly')
            return True
        else:
            print(f'   ❌ Script execution failed')
            return False
    
    def test_vault_structure(self):
        """Test vault folder structure"""
        print('Checking vault structure...')
        
        required_folders = [
            'Briefings',
            'Logs',
            'Pending_Approval',
            'Approved',
            'Done',
            'Needs_Action'
        ]
        
        all_exist = True
        for folder in required_folders:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                print(f'   ✅ {folder}/')
            else:
                print(f'   ⚠️ {folder}/ not found')
                all_exist = False
        
        return all_exist
    
    def test_env_credentials(self):
        """Test .env file has Gold Tier credentials"""
        print('Checking .env credentials...')
        
        env_path = Path('.env')
        if not env_path.exists():
            print('   ❌ .env file not found')
            return False
        
        content = env_path.read_text()
        
        required_vars = [
            'ODOO_URL',
            'ODOO_DB',
            'ODOO_USERNAME',
            'ODOO_PASSWORD',
            'FACEBOOK_PAGE_ID',
            'FACEBOOK_ACCESS_TOKEN',
            'INSTAGRAM_ACCOUNT_ID'
        ]
        
        all_present = True
        for var in required_vars:
            if var in content:
                # Check if it has a value (not just commented out)
                for line in content.split('\n'):
                    if line.startswith(var) and '=' in line:
                        value = line.split('=', 1)[1].strip()
                        if value and not value.startswith('#'):
                            print(f'   ✅ {var}')
                            break
                else:
                    print(f'   ⚠️ {var} commented out or empty')
                    all_present = False
            else:
                print(f'   ❌ {var} missing')
                all_present = False
        
        return all_present
    
    def run_all_tests(self):
        """Run all verification tests"""
        print('\n' + '='*60)
        print('🔍 Gold Tier Verification')
        print('='*60)
        print(f'Vault: {self.vault_path}')
        print(f'Time: {datetime.now().isoformat()}')
        
        # Run tests
        self.test('Vault Structure', self.test_vault_structure)
        self.test('Environment Credentials', self.test_env_credentials)
        self.test('Odoo Docker Setup', self.test_odoo_docker)
        self.test('Odoo MCP Server', self.test_odoo_mcp)
        self.test('Facebook MCP Server', self.test_facebook_mcp)
        self.test('Ralph Wiggum Loop', self.test_ralph_wiggum)
        self.test('CEO Briefing Generator', self.test_ceo_briefing)
        self.test('Audit Logger', self.test_audit_logger)
        self.test('Master Orchestrator', self.test_orchestrator)
        
        # Print summary
        print('\n' + '='*60)
        print('📊 Verification Summary')
        print('='*60)
        
        for name, result in self.results.items():
            status = '✅' if result == 'PASSED' else '❌'
            print(f'{status} {name}: {result}')
        
        print('\n' + '='*60)
        print(f'Total: {self.passed} passed, {self.failed} failed')
        print('='*60)
        
        if self.failed == 0:
            print('\n🎉 All tests passed! Gold Tier is fully operational.')
        else:
            print(f'\n⚠️ {self.failed} test(s) failed. Please fix issues before using Gold Tier.')
        
        return self.failed == 0


def main():
    """Main entry point"""
    verifier = GoldTierVerifier()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
