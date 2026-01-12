"""
API Integrations
Handles connections to Outreach, Salesforce, and Orum
"""

import os
import requests
from simple_salesforce import Salesforce
from datetime import datetime
import json


class OutreachAPI:
    """Handle Outreach API operations"""

    def __init__(self, demo_mode=None):
        """Initialize Outreach API connection"""
        self.api_key = os.getenv('OUTREACH_API_KEY')
        self.api_url = os.getenv('OUTREACH_API_URL', 'https://api.outreach.io/api/v2')

        # Auto-detect demo mode if no API key
        self.demo_mode = demo_mode if demo_mode is not None else (not self.api_key)

        if self.demo_mode:
            print("   📋 Outreach: Running in DEMO mode")
            return

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def schedule_email(self, prospect_email, subject, body, send_time):
        """
        Schedule an email in Outreach

        Args:
            prospect_email (str): Recipient email address
            subject (str): Email subject line
            body (str): Email body content
            send_time (str): ISO format datetime when to send

        Returns:
            dict: API response with email details
        """
        if self.demo_mode:
            print(f"   [DEMO] Would schedule email to {prospect_email}")
            return {'success': True, 'demo': True}

        # First, find or create the prospect
        prospect = self._find_or_create_prospect(prospect_email)
        
        if not prospect:
            return {'success': False, 'error': 'Could not find or create prospect'}
        
        # Create the mailing (one-off email in Outreach)
        mailing_data = {
            'data': {
                'type': 'mailing',
                'attributes': {
                    'subject': subject,
                    'body': body,
                    'scheduledAt': send_time,
                    'mailingType': 'one_off'
                },
                'relationships': {
                    'prospect': {
                        'data': {
                            'type': 'prospect',
                            'id': prospect['id']
                        }
                    }
                }
            }
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/mailings',
                headers=self.headers,
                json=mailing_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Email scheduled in Outreach for {send_time}")
                return {'success': True, 'data': response.json()}
            else:
                print(f"❌ Failed to schedule email: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ Error scheduling email: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_to_sequence(self, prospect_email, sequence_name):
        """
        Add a prospect to a specific sequence

        Args:
            prospect_email (str): Prospect's email
            sequence_name (str): Name of the sequence to add them to

        Returns:
            dict: API response
        """
        if self.demo_mode:
            print(f"   [DEMO] Would add {prospect_email} to sequence '{sequence_name}'")
            return {'success': True, 'demo': True}

        # Find the prospect
        prospect = self._find_or_create_prospect(prospect_email)
        if not prospect:
            return {'success': False, 'error': 'Could not find prospect'}
        
        # Find the sequence
        sequence = self._find_sequence(sequence_name)
        if not sequence:
            return {'success': False, 'error': f'Could not find sequence: {sequence_name}'}
        
        # Add prospect to sequence
        sequence_state_data = {
            'data': {
                'type': 'sequenceState',
                'relationships': {
                    'prospect': {
                        'data': {'type': 'prospect', 'id': prospect['id']}
                    },
                    'sequence': {
                        'data': {'type': 'sequence', 'id': sequence['id']}
                    }
                }
            }
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/sequenceStates',
                headers=self.headers,
                json=sequence_state_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Added to sequence: {sequence_name}")
                return {'success': True}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_from_all_sequences(self, prospect_email):
        """
        Remove prospect from all active sequences (for dead ends)

        Args:
            prospect_email (str): Prospect's email

        Returns:
            dict: Result of the operation
        """
        if self.demo_mode:
            print(f"   [DEMO] Would remove {prospect_email} from all sequences")
            return {'success': True, 'count': 2, 'demo': True}

        prospect = self._find_or_create_prospect(prospect_email)
        if not prospect:
            return {'success': False, 'error': 'Could not find prospect'}
        
        # Find all active sequence states for this prospect
        try:
            response = requests.get(
                f'{self.api_url}/sequenceStates',
                headers=self.headers,
                params={'filter[prospectId]': prospect['id'], 'filter[state]': 'active'}
            )
            
            if response.status_code == 200:
                sequence_states = response.json().get('data', [])
                
                # Pause each active sequence state
                for state in sequence_states:
                    self._pause_sequence_state(state['id'])
                
                print(f"✅ Removed from {len(sequence_states)} sequences")
                return {'success': True, 'count': len(sequence_states)}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _find_or_create_prospect(self, email):
        """Internal method to find or create a prospect"""
        
        # Search for existing prospect
        try:
            response = requests.get(
                f'{self.api_url}/prospects',
                headers=self.headers,
                params={'filter[emails]': email}
            )
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    return data[0]
            
            # If not found, you might create them here
            # For now, return None if not found
            return None
            
        except Exception as e:
            print(f"Error finding prospect: {str(e)}")
            return None
    
    def _find_sequence(self, sequence_name):
        """Internal method to find a sequence by name"""
        
        try:
            response = requests.get(
                f'{self.api_url}/sequences',
                headers=self.headers,
                params={'filter[name]': sequence_name}
            )
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    return data[0]
            
            return None
            
        except Exception as e:
            print(f"Error finding sequence: {str(e)}")
            return None
    
    def _pause_sequence_state(self, sequence_state_id):
        """Internal method to pause a sequence state"""
        
        try:
            update_data = {
                'data': {
                    'type': 'sequenceState',
                    'id': sequence_state_id,
                    'attributes': {
                        'state': 'paused'
                    }
                }
            }
            
            response = requests.patch(
                f'{self.api_url}/sequenceStates/{sequence_state_id}',
                headers=self.headers,
                json=update_data
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            print(f"Error pausing sequence: {str(e)}")
            return False


class SalesforceAPI:
    """Handle Salesforce API operations"""

    def __init__(self, demo_mode=None):
        """Initialize Salesforce connection"""
        username = os.getenv('SALESFORCE_USERNAME')
        password = os.getenv('SALESFORCE_PASSWORD')
        security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')

        # Auto-detect demo mode if credentials missing
        self.demo_mode = demo_mode if demo_mode is not None else (not all([username, password, security_token]))

        if self.demo_mode:
            print("   📋 Salesforce: Running in DEMO mode")
            return

        try:
            self.sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token
            )
            print("✅ Connected to Salesforce")
        except Exception as e:
            print(f"❌ Failed to connect to Salesforce: {str(e)}")
            raise
    
    def get_contact_info(self, email):
        """
        Get contact information from Salesforce

        Args:
            email (str): Contact's email address

        Returns:
            dict: Contact information (name, company, etc.)
        """
        if self.demo_mode:
            # Return mock data for demo
            name_part = email.split('@')[0] if email else 'demo'
            return {
                'id': 'DEMO_001',
                'first_name': name_part.split('.')[0].title() if '.' in name_part else name_part.title(),
                'last_name': name_part.split('.')[-1].title() if '.' in name_part else 'User',
                'email': email,
                'company': 'Demo Company',
                'phone': '555-0100',
                'title': 'Demo Contact'
            }

        try:
            # Query for contact
            query = f"SELECT Id, FirstName, LastName, Email, Account.Name, Phone, Title FROM Contact WHERE Email = '{email}' LIMIT 1"
            result = self.sf.query(query)
            
            if result['records']:
                contact = result['records'][0]
                return {
                    'id': contact['Id'],
                    'first_name': contact.get('FirstName', ''),
                    'last_name': contact.get('LastName', ''),
                    'email': contact.get('Email', ''),
                    'company': contact.get('Account', {}).get('Name', '') if contact.get('Account') else '',
                    'phone': contact.get('Phone', ''),
                    'title': contact.get('Title', '')
                }
            else:
                # Try Lead instead
                query = f"SELECT Id, FirstName, LastName, Email, Company, Phone, Title FROM Lead WHERE Email = '{email}' LIMIT 1"
                result = self.sf.query(query)
                
                if result['records']:
                    lead = result['records'][0]
                    return {
                        'id': lead['Id'],
                        'first_name': lead.get('FirstName', ''),
                        'last_name': lead.get('LastName', ''),
                        'email': lead.get('Email', ''),
                        'company': lead.get('Company', ''),
                        'phone': lead.get('Phone', ''),
                        'title': lead.get('Title', ''),
                        'is_lead': True
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting contact info: {str(e)}")
            return None
    
    def log_call_activity(self, contact_id, call_transcript, analysis_result):
        """
        Log a call as a Task/Activity in Salesforce

        Args:
            contact_id (str): Salesforce Contact or Lead ID
            call_transcript (str): Full call transcript
            analysis_result (dict): Analysis from Claude

        Returns:
            dict: Created task details
        """
        if self.demo_mode:
            print(f"   [DEMO] Would log call activity for contact {contact_id}")
            return {'success': True, 'task_id': 'DEMO_TASK_001', 'demo': True}

        try:
            # Create a Task
            task_data = {
                'WhoId': contact_id,
                'Subject': f"Call - {analysis_result['decision']}",
                'Status': 'Completed',
                'ActivityDate': datetime.now().strftime('%Y-%m-%d'),
                'Description': f"""Call Outcome: {analysis_result['decision']}
Confidence: {analysis_result['confidence']}/10
Reasoning: {analysis_result['reasoning']}

Next Action: {analysis_result['next_action']}

Full Transcript:
{call_transcript[:30000]}"""  # Salesforce has char limits
            }
            
            result = self.sf.Task.create(task_data)
            
            if result['success']:
                print(f"✅ Logged call activity in Salesforce")
                return {'success': True, 'task_id': result['id']}
            else:
                print(f"❌ Failed to log call: {result}")
                return {'success': False}
                
        except Exception as e:
            print(f"❌ Error logging call: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_lead_status(self, contact_id, status, is_lead=False):
        """
        Update lead/contact status based on call outcome

        Args:
            contact_id (str): Salesforce ID
            status (str): New status (e.g., "Qualified", "Disqualified")
            is_lead (bool): Whether this is a Lead or Contact

        Returns:
            bool: Success status
        """
        if self.demo_mode:
            print(f"   [DEMO] Would update status to '{status}' for {contact_id}")
            return True

        try:
            if is_lead:
                self.sf.Lead.update(contact_id, {'Status': status})
            else:
                # For contacts, you might update a custom field
                # Adjust this based on your Salesforce setup
                pass
            
            print(f"✅ Updated status to: {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating status: {str(e)}")
            return False


class OrumAPI:
    """Handle Orum API operations"""

    def __init__(self, demo_mode=None):
        """Initialize Orum API connection"""
        self.api_key = os.getenv('ORUM_API_KEY')
        self.api_url = os.getenv('ORUM_API_URL', 'https://api.orum.com/v1')

        # Auto-detect demo mode if no API key
        self.demo_mode = demo_mode if demo_mode is not None else (not self.api_key)

        if self.demo_mode:
            print("   📋 Orum: Running in DEMO mode")
            return

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_recent_transcripts(self, minutes=30):
        """
        Get call transcripts from the last X minutes

        Args:
            minutes (int): How far back to look for transcripts

        Returns:
            list: List of transcript objects
        """
        if self.demo_mode:
            print(f"   [DEMO] Would fetch transcripts from last {minutes} minutes")
            return []

        try:
            # Calculate timestamp
            from datetime import datetime, timedelta
            since = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            response = requests.get(
                f'{self.api_url}/transcripts',
                headers=self.headers,
                params={'since': since}
            )
            
            if response.status_code == 200:
                transcripts = response.json().get('data', [])
                print(f"✅ Found {len(transcripts)} new transcripts")
                return transcripts
            else:
                print(f"❌ Failed to get transcripts: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting transcripts: {str(e)}")
            return []
    
    def get_transcript_by_id(self, transcript_id):
        """
        Get a specific transcript by ID

        Args:
            transcript_id (str): The transcript ID

        Returns:
            dict: Transcript data
        """
        if self.demo_mode:
            print(f"   [DEMO] Would fetch transcript {transcript_id}")
            return {'id': transcript_id, 'transcript': 'Demo transcript', 'demo': True}

        try:
            response = requests.get(
                f'{self.api_url}/transcripts/{transcript_id}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get transcript: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting transcript: {str(e)}")
            return None


# Test connections
if __name__ == "__main__":
    print("Testing API connections...\n")
    
    try:
        print("1. Testing Salesforce...")
        sf = SalesforceAPI()
        print("   ✅ Salesforce connected\n")
    except Exception as e:
        print(f"   ❌ Salesforce failed: {str(e)}\n")
    
    try:
        print("2. Testing Outreach...")
        outreach = OutreachAPI()
        print("   ✅ Outreach initialized\n")
    except Exception as e:
        print(f"   ❌ Outreach failed: {str(e)}\n")
    
    try:
        print("3. Testing Orum...")
        orum = OrumAPI()
        print("   ✅ Orum initialized\n")
    except Exception as e:
        print(f"   ❌ Orum failed: {str(e)}\n")
