#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Email Reply Generator - Uses Qwen Code to generate contextual replies.

This module generates intelligent, contextual email replies by analyzing:
1. The received email content
2. Sender information
3. Email subject and context
4. Business goals and company handbook (if available)

Usage:
    from intelligent_reply import generate_intelligent_reply
    reply = generate_intelligent_reply(email_data)
"""

import re
from pathlib import Path
from typing import Dict, Optional


class IntelligentReplyGenerator:
    """Generates intelligent, contextual email replies."""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.business_goals = self._load_business_goals()
        self.company_handbook = self._load_company_handbook()

    def _load_business_goals(self) -> str:
        """Load business goals if available."""
        if self.vault_path:
            goals_file = self.vault_path / 'Business_Goals.md'
            if goals_file.exists():
                return goals_file.read_text()
        return ""

    def _load_company_handbook(self) -> str:
        """Load company handbook if available."""
        if self.vault_path:
            handbook_file = self.vault_path / 'Company_Handbook.md'
            if handbook_file.exists():
                return handbook_file.read_text()
        return ""

    def analyze_email(self, email_data: dict) -> dict:
        """Analyze email to understand context and intent."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        from_email = email_data.get('from', '')
        from_name = from_email.split('<')[0].strip()

        # Determine email type and intent
        analysis = {
            'type': 'general',
            'intent': 'informational',
            'tone': 'professional',
            'urgency': 'normal',
            'requires_action': False,
            'key_topics': [],
            'questions_asked': [],
            'sender_relationship': 'unknown',
            'is_casual': False,
            'is_invitation': False
        }

        # Check for invitations FIRST (before casual greetings)
        invitation_keywords = [
            'lunch', 'dinner', 'breakfast', 'coffee', 'meet up', 'meetup',
            'join me', 'joining me', 'get together', 'hang out',
            'are you free', 'are you available', 'would you like',
            'interested in', 'want to', 'do you want', 'lets meet',
            "let's meet", 'grab lunch', 'grab coffee', 'invite'
        ]
        
        for keyword in invitation_keywords:
            if keyword in body or keyword in subject:
                analysis['is_invitation'] = True
                analysis['type'] = 'invitation'
                analysis['requires_action'] = True
                break

        # Check for casual/greeting emails (only if NOT an invitation)
        if not analysis['is_invitation']:
            casual_greetings = [
                'hi', 'hello', 'hey', 'how are you', "how's it going", 'whats up',
                'what\'s up', 'how are things', 'hope you are well', 'greetings'
            ]
            
            # Check if subject or body is JUST a casual greeting (very short)
            subject_clean = subject.strip().lower().replace('re:', '').replace('fwd:', '').strip()
            body_clean = body.strip().lower()
            
            # Only classify as casual if it's truly just a greeting (under 30 chars, no questions)
            is_short_greeting = len(body_clean) < 30 and \
                               any(greeting in body_clean for greeting in casual_greetings)
            
            if is_short_greeting:
                analysis['is_casual'] = True
                analysis['type'] = 'casual_greeting'
                analysis['tone'] = 'casual'

        # Check if it's a forward
        if 'forward' in subject or 'fwd:' in email_data.get('subject', '').lower():
            analysis['type'] = 'forward'
            analysis['intent'] = 'sharing_information'

        # Detect questions
        question_patterns = [
            r'\?',
            r'can you',
            r'could you',
            r'would you',
            r'are you able',
            r'when can',
            r'how can',
            r'what do you think',
            r'please let me know',
            r'please confirm'
        ]
        for pattern in question_patterns:
            if re.search(pattern, body) or re.search(pattern, subject):
                analysis['requires_action'] = True
                analysis['intent'] = 'requesting_response'
                break

        # Detect scheduling requests (formal meetings)
        if not analysis['is_invitation']:
            schedule_keywords = ['meeting', 'schedule', 'calendar', 'book', 'appointment', 'time slot', 'conference']
            for keyword in schedule_keywords:
                if keyword in body or keyword in subject:
                    analysis['type'] = 'scheduling'
                    analysis['intent'] = 'requesting_meeting'
                    analysis['requires_action'] = True
                    break

        # Detect urgency
        urgency_keywords = ['urgent', 'asap', 'immediately', 'as soon as possible', 'deadline', 'tomorrow', 'today']
        for keyword in urgency_keywords:
            if keyword in body or keyword in subject:
                analysis['urgency'] = 'high'
                break

        # Detect questions specifically asked
        if '?' in email_data.get('body', ''):
            sentences = email_data.get('body', '').replace('\n', '. ').split('.')
            for sentence in sentences:
                if '?' in sentence:
                    analysis['questions_asked'].append(sentence.strip())

        # Extract key topics (simple keyword extraction)
        topic_keywords = [
            'project', 'update', 'report', 'build', 'development',
            'google', 'developer', 'program', 'newsletter',
            'invoice', 'payment', 'budget', 'proposal',
            'feedback', 'review', 'approval',
            'introduction', 'networking', 'connection',
            'congratulations', 'achievement', 'milestone',
            'lunch', 'coffee', 'meetup', 'event'
        ]
        for topic in topic_keywords:
            if topic in body or topic in subject:
                analysis['key_topics'].append(topic)

        # Determine sender relationship
        if 'personal' in email_data.get('labels', '').lower():
            analysis['sender_relationship'] = 'personal'
        elif 'work' in email_data.get('labels', '').lower():
            analysis['sender_relationship'] = 'professional'

        return analysis

    def generate_reply(self, email_data: dict) -> str:
        """Generate an intelligent, contextual reply."""
        analysis = self.analyze_email(email_data)

        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        from_name = email_data.get('from', '').split('<')[0].strip()

        # Generate reply based on analysis
        reply = self._build_reply(analysis, email_data)

        return reply

    def _build_reply(self, analysis: dict, email_data: dict) -> str:
        """Build a contextual reply based on email analysis."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        # Invitation (lunch, coffee, meetup)
        if analysis['is_invitation']:
            return self._reply_invitation(analysis, email_data)

        # Casual greeting
        elif analysis['is_casual']:
            return self._reply_casual_greeting(analysis, email_data)

        # Forward acknowledgment
        elif analysis['type'] == 'forward':
            return self._reply_forward(analysis, email_data)

        # Scheduling request
        elif analysis['type'] == 'scheduling':
            return self._reply_scheduling(analysis, email_data)

        # Questions asked
        elif analysis['requires_action'] and analysis['questions_asked']:
            return self._reply_to_questions(analysis, email_data)

        # Newsletter/Program update
        elif any(topic in analysis['key_topics'] for topic in ['google', 'developer', 'program', 'newsletter']):
            return self._reply_newsletter(analysis, email_data)

        # General professional email
        else:
            return self._reply_general(analysis, email_data)

    def _reply_invitation(self, analysis: dict, email_data: dict) -> str:
        """Reply to invitations (lunch, coffee, meetup, etc.)."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        body = email_data.get('body', '')
        subject = email_data.get('subject', '')

        # Detect what the invitation is about
        body_lower = body.lower()
        event_type = "meet up"
        
        if 'lunch' in body_lower:
            event_type = "lunch"
        elif 'dinner' in body_lower:
            event_type = "dinner"
        elif 'breakfast' in body_lower:
            event_type = "breakfast"
        elif 'coffee' in body_lower:
            event_type = "coffee"

        return f"""Hi {from_name},

Thanks for the invitation! I'd love to join you for {event_type} today.

What time and place did you have in mind? Let me know the details and I'll make sure I'm available.

Looking forward to it!

Best"""

    def _reply_casual_greeting(self, analysis: dict, email_data: dict) -> str:
        """Reply to casual greeting emails."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        body = email_data.get('body', '').lower()
        subject = email_data.get('subject', '').lower()

        # Check if they asked "how are you"
        asks_how_are_you = 'how are you' in body or "how's it going" in body or 'how are things' in body

        if asks_how_are_you:
            return f"""Hi {from_name},

Hey! I'm doing great, thanks for asking! 😊

Hope you're doing well too. What's new with you?

Best"""
        else:
            return f"""Hi {from_name},

Hey! Great to hear from you! 

Hope everything's going well on your end. What's up?

Best"""

    def _reply_forward(self, analysis: dict, email_data: dict) -> str:
        """Reply to forwarded email."""
        from_name = email_data.get('from', '').split('<')[0].strip()

        return f"""Hi {from_name},

Thanks for forwarding this to me. I've reviewed the information you shared.

I'll look through the details and get back to you if I have any questions or if there's anything I need to follow up on.

I appreciate you keeping me in the loop.

Best regards"""

    def _reply_scheduling(self, analysis: dict, email_data: dict) -> str:
        """Reply to scheduling request."""
        from_name = email_data.get('from', '').split('<')[0].strip()

        return f"""Hi {from_name},

Thanks for reaching out about scheduling. I'd be happy to set up a time to connect.

Let me check my calendar and I'll get back to you shortly with some available time slots that work for me.

I'll respond within the next few hours with my availability.

Talk soon,
"""

    def _reply_to_questions(self, analysis: dict, email_data: dict) -> str:
        """Reply when questions are asked."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        questions = analysis['questions_asked']

        reply = f"""Hi {from_name},

Thank you for your email. I appreciate you reaching out.

"""
        if questions:
            reply += "Regarding your questions:\n"
            for i, question in enumerate(questions[:3], 1):
                reply += f"\n{i}. {question.strip()}\n"
            reply += "\nI'm looking into these and will get back to you with detailed answers as soon as possible.\n"
        else:
            reply += "I'm reviewing your questions and will provide detailed answers shortly.\n"

        reply += """
Thank you for your patience.

Best regards"""

        return reply

    def _reply_newsletter(self, analysis: dict, email_data: dict) -> str:
        """Reply to newsletter/program updates."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        subject = email_data.get('subject', '')

        return f"""Hi {from_name},

Thank you for sharing this update. I've received the information and appreciate you keeping me informed about the program.

I'll review the details and take advantage of the resources and opportunities mentioned.

Thanks again for the update!

Best regards"""

    def _reply_general(self, analysis: dict, email_data: dict) -> str:
        """Reply to general emails."""
        from_name = email_data.get('from', '').split('<')[0].strip()
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        # Try to extract key points from the email
        key_points = []
        if body:
            sentences = body.replace('\n', '. ').split('.')
            key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]

        reply = f"""Hi {from_name},

Thank you for your email regarding "{subject}".

I've received your message and am reviewing the details. I'll get back to you with a comprehensive response shortly.

"""
        if analysis['urgency'] == 'high':
            reply += "I understand this is time-sensitive and will prioritize it accordingly.\n\n"

        reply += "Best regards"

        return reply


def generate_intelligent_reply(email_data: dict, vault_path: str = None) -> str:
    """
    Generate an intelligent reply for the given email.

    Args:
        email_data: Dictionary with email fields (from, subject, body, etc.)
        vault_path: Path to vault for loading business context

    Returns:
        Generated reply string
    """
    generator = IntelligentReplyGenerator(vault_path)
    return generator.generate_reply(email_data)


def main():
    """Test the intelligent reply generator."""
    # Example email
    test_email = {
        'from': 'John Doe <john@example.com>',
        'subject': 'Project Update - Q1 Review',
        'body': 'Hi,\n\nI wanted to share the Q1 project update with you. We\'ve made good progress on the development front.\n\nCan you review the attached report and provide feedback by Friday?\n\nThanks,\nJohn',
        'labels': 'INBOX, IMPORTANT'
    }

    print("Generated Reply:")
    print("=" * 60)
    reply = generate_intelligent_reply(test_email)
    print(reply)
    print("=" * 60)


if __name__ == '__main__':
    main()
