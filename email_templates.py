"""
Email Templates
Customizable templates for different scenarios
"""

import os
from datetime import datetime


class EmailTemplates:
    """
    Email templates for different prospect scenarios
    You can customize these to match your voice and style!
    """
    
    def __init__(self):
        """Load personalization from environment variables"""
        self.your_name = os.getenv('YOUR_NAME', 'Your Name')
        self.your_email = os.getenv('YOUR_EMAIL', 'your@email.com')
        self.your_title = os.getenv('YOUR_TITLE', 'Sales Development Representative')
        self.your_company = os.getenv('YOUR_COMPANY', 'Company Name')
        self.your_phone = os.getenv('YOUR_PHONE', '')
        self.calendar_link = os.getenv('YOUR_CALENDAR_LINK', 'https://calendly.com/yourname')
    
    def generate_interested_email(self, prospect_data, call_analysis):
        """
        Generate email for INTERESTED prospects
        
        Args:
            prospect_data (dict): Prospect info from Salesforce (name, company, etc.)
            call_analysis (dict): Results from conversation analysis
            
        Returns:
            dict: Email with subject, body, and metadata
        """
        
        first_name = prospect_data.get('first_name', 'there')
        company = prospect_data.get('company', 'your institution')
        
        # Extract topics mentioned in the call
        topics = call_analysis.get('email_topics', [])
        topic_text = topics[0] if topics else "our conversation"
        
        # Create personalized opener based on analysis
        opener = self._create_opener(call_analysis)
        
        subject = f"Following up on {topic_text}"
        
        body = f"""Hi {first_name},

{opener}

{self._generate_relevant_content(call_analysis, prospect_data)}

I'd love to show you how we've helped similar institutions. {self._generate_calendar_cta(first_name)}

Best,
{self.your_name}
{self.your_title}
{self.your_company}
{self.your_phone}
"""
        
        return {
            'subject': subject,
            'body': body,
            'type': 'interested',
            'send_time': self._calculate_send_time()
        }
    
    def generate_warm_email(self, prospect_data, call_analysis):
        """
        Generate email for WARM prospects (interested but not ready)
        More subtle, educational approach
        """
        
        first_name = prospect_data.get('first_name', 'there')
        company = prospect_data.get('company', 'your institution')
        
        subject = f"Resource for {company}"
        
        body = f"""Hi {first_name},

Thanks for taking the time to chat earlier. I know you mentioned you're not looking at this right now, but I wanted to share a quick resource in case it's helpful down the road.

{self._generate_case_study_link(prospect_data)}

No pressure at all - just wanted to make sure you had this. Feel free to reach out anytime if you'd like to chat further.

Best,
{self.your_name}
{self.your_title}
"""
        
        return {
            'subject': subject,
            'body': body,
            'type': 'warm',
            'send_time': self._calculate_send_time(days_ahead=2)  # Send in 2 days
        }
    
    def _create_opener(self, call_analysis):
        """Create a personalized opening line based on the call"""
        
        reasoning = call_analysis.get('reasoning', '')
        
        # Try to extract what they were interested in
        if 'budget' in reasoning.lower() or 'savings' in reasoning.lower():
            return "Great speaking with you about how Pathify can help reduce costs while improving the student experience."
        elif 'student' in reasoning.lower() or 'engagement' in reasoning.lower():
            return "I really enjoyed our conversation about boosting student engagement on campus."
        elif 'timeline' in reasoning.lower():
            return "Thanks for chatting today! I know you mentioned looking at this for the upcoming semester."
        else:
            return "Thanks for taking the time to speak with me today about Pathify."
    
    def _generate_relevant_content(self, call_analysis, prospect_data):
        """Generate relevant content based on what was discussed"""
        
        # Get email topics from analysis
        topics = call_analysis.get('email_topics', [])
        
        # Default content blocks
        content_blocks = {
            'savings': "Schools like yours typically save 35-45% on their student-facing tech stack by consolidating redundant systems.",
            'engagement': "Our clients see an average 80% increase in student engagement when they streamline access to resources.",
            'implementation': "Implementation typically takes 6-8 weeks, and we handle the heavy lifting of data migration and integrations.",
            'case_study': "University of Pacific went from 28 systems down to 5, saving $400K annually while doubling student app engagement.",
            'integration': "Pathify integrates seamlessly with Canvas, Workday, Slate, and 200+ other common campus systems."
        }
        
        # Pick the most relevant content
        if any('budget' in t.lower() or 'cost' in t.lower() or 'savings' in t.lower() for t in topics):
            return content_blocks['savings'] + "\n\n" + content_blocks['case_study']
        elif any('student' in t.lower() or 'engagement' in t.lower() for t in topics):
            return content_blocks['engagement'] + "\n\n" + content_blocks['case_study']
        elif any('implement' in t.lower() or 'timeline' in t.lower() for t in topics):
            return content_blocks['implementation']
        elif any('integrat' in t.lower() or 'canvas' in t.lower() or 'lms' in t.lower() for t in topics):
            return content_blocks['integration']
        else:
            return content_blocks['case_study']
    
    def _generate_case_study_link(self, prospect_data):
        """Generate a relevant case study based on prospect's profile"""
        
        # In a real implementation, you'd select based on industry, size, etc.
        return "Here's a case study from University of Pacific that shows the impact: [LINK TO CASE STUDY]"
    
    def _generate_calendar_cta(self, first_name):
        """Generate call-to-action with calendar link"""
        
        return f"Find a time that works for you here: {self.calendar_link}"
    
    def _calculate_send_time(self, days_ahead=1):
        """
        Calculate when to send the email
        Default: Tomorrow at 9 AM in their timezone
        """
        from datetime import datetime, timedelta
        import pytz
        
        # Get timezone from env (default to Central)
        timezone = os.getenv('TIMEZONE', 'America/Chicago')
        tz = pytz.timezone(timezone)
        
        # Get default send time from env (default 9 AM)
        send_time = os.getenv('DEFAULT_EMAIL_TIME', '09:00')
        hour, minute = map(int, send_time.split(':'))
        
        # Calculate send time
        now = datetime.now(tz)
        send_date = now + timedelta(days=days_ahead)
        send_datetime = send_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return send_datetime.isoformat()


# Example usage (for testing)
if __name__ == "__main__":
    print("Testing Email Templates...")
    
    # Sample data
    prospect_data = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane.doe@university.edu',
        'company': 'Example University'
    }
    
    call_analysis = {
        'decision': 'INTERESTED',
        'reasoning': 'Asked about budget savings and implementation timeline',
        'email_topics': ['Cost savings', 'Implementation timeline']
    }
    
    # Generate email
    templates = EmailTemplates()
    email = templates.generate_interested_email(prospect_data, call_analysis)
    
    print(f"\n📧 SUBJECT: {email['subject']}")
    print(f"\n{email['body']}")
    print(f"\n⏰ SEND TIME: {email['send_time']}")
