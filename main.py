"""
Main SDR Automation Script
This is the main file that runs the automation
"""

import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Import our custom modules
from analyzer import ConversationAnalyzer
from email_templates import EmailTemplates
from integrations import OutreachAPI, SalesforceAPI, OrumAPI
from transcriber import AudioTranscriber

# Supported audio formats
AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm'}


class SDRAutomation:
    """
    Main automation class that orchestrates everything
    """
    
    def __init__(self):
        """Initialize all components"""
        
        print("🚀 Initializing SDR Automation...")
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize components
        try:
            self.analyzer = ConversationAnalyzer()
            self.templates = EmailTemplates()
            self.outreach = OutreachAPI()
            self.salesforce = SalesforceAPI()
            self.orum = OrumAPI()
            self.transcriber = None  # Lazy-load when needed

            print("✅ All systems initialized!\n")
            
        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            print("💡 Make sure your .env file is configured correctly")
            sys.exit(1)
        
        # Load settings
        self.auto_send = os.getenv('AUTO_SEND_EMAILS', 'false').lower() == 'true'
        self.auto_remove_dead = os.getenv('AUTO_REMOVE_DEAD_ENDS', 'true').lower() == 'true'
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))  # minutes
    
    def process_call(self, transcript, prospect_email=None):
        """
        Process a single call transcript through the entire workflow
        
        Args:
            transcript (str): The call transcript text
            prospect_email (str, optional): Email of the prospect
            
        Returns:
            dict: Results of the processing
        """
        
        print("=" * 60)
        print(f"📞 PROCESSING NEW CALL")
        print("=" * 60)
        
        # Step 1: Analyze the conversation
        print("\n1️⃣  Analyzing conversation...")
        analysis = self.analyzer.analyze_call(transcript)
        
        decision = analysis['decision']
        emoji = self.analyzer.get_decision_emoji(decision)
        
        print(f"   {emoji} Decision: {decision}")
        print(f"   💯 Confidence: {analysis['confidence']}/10")
        print(f"   📝 Reasoning: {analysis['reasoning']}")
        
        # Step 2: Get prospect info from Salesforce
        print("\n2️⃣  Looking up prospect in Salesforce...")
        prospect_data = None
        
        if prospect_email:
            prospect_data = self.salesforce.get_contact_info(prospect_email)
            
            if prospect_data:
                print(f"   ✅ Found: {prospect_data['first_name']} {prospect_data['last_name']}")
                print(f"   🏢 Company: {prospect_data['company']}")
            else:
                print(f"   ⚠️  No record found for {prospect_email}")
                prospect_data = {'email': prospect_email, 'first_name': 'there'}
        else:
            print("   ⚠️  No email provided, skipping Salesforce lookup")
        
        # Step 3: Take action based on decision
        print(f"\n3️⃣  Taking action for {decision} prospect...")
        
        if decision == 'INTERESTED' or decision == 'WARM':
            self._handle_interested_prospect(analysis, prospect_data)
            
        elif decision == 'NURTURE':
            self._handle_nurture_prospect(analysis, prospect_data)
            
        elif decision == 'DEAD_END':
            self._handle_dead_end_prospect(analysis, prospect_data)
        
        # Note: Salesforce is read-only (just pulls prospect info)
        # No logging or status updates are made
        
        print("\n" + "=" * 60)
        print("✅ PROCESSING COMPLETE")
        print("=" * 60 + "\n")
        
        return {
            'analysis': analysis,
            'prospect': prospect_data,
            'success': True
        }
    
    def _handle_interested_prospect(self, analysis, prospect_data):
        """Handle INTERESTED or WARM prospects"""
        
        if not prospect_data:
            print("   ⚠️  Cannot send email - no prospect data")
            return
        
        # Generate personalized email
        if analysis['decision'] == 'INTERESTED':
            email = self.templates.generate_interested_email(prospect_data, analysis)
        else:  # WARM
            email = self.templates.generate_warm_email(prospect_data, analysis)
        
        print(f"   ✉️  Email generated:")
        print(f"      Subject: {email['subject']}")
        print(f"      Send time: {email['send_time']}")
        
        # Schedule in Outreach
        if self.auto_send:
            print("   📤 Scheduling email in Outreach...")
            result = self.outreach.schedule_email(
                prospect_data['email'],
                email['subject'],
                email['body'],
                email['send_time']
            )
            
            if result['success']:
                print("   ✅ Email scheduled!")
            else:
                print(f"   ❌ Failed to schedule: {result.get('error')}")
        else:
            print("   📝 Email drafted (auto-send is off)")
            print("\n   Preview:")
            print("   " + "-" * 50)
            print(f"   {email['body'][:200]}...")
            print("   " + "-" * 50)
    
    def _handle_nurture_prospect(self, analysis, prospect_data):
        """Handle NURTURE prospects (future follow-up)"""
        
        print("   📅 Adding to long-term nurture sequence...")
        
        if prospect_data and prospect_data.get('email'):
            # Add to a nurture sequence in Outreach
            result = self.outreach.add_to_sequence(
                prospect_data['email'],
                'Long-Term Nurture'  # You can customize this
            )
            
            if result['success']:
                print("   ✅ Added to nurture sequence")
            else:
                print(f"   ⚠️  Could not add to sequence: {result.get('error')}")
    
    def _handle_dead_end_prospect(self, analysis, prospect_data):
        """Handle DEAD_END prospects"""
        
        print("   🛑 Processing dead end...")
        
        if prospect_data and prospect_data.get('email'):
            # Remove from all active sequences
            if self.auto_remove_dead:
                print("   🔴 Removing from all sequences...")
                result = self.outreach.remove_from_all_sequences(prospect_data['email'])
                
                if result['success']:
                    print(f"   ✅ Removed from {result.get('count', 0)} sequences")
                else:
                    print(f"   ⚠️  Could not remove: {result.get('error')}")
            else:
                print("   ⚠️  Auto-remove is off, keeping in sequences")
        
        print("   ✅ Marked as disqualified")
    
    def run_manual(self, input_file):
        """
        Process a single transcript or audio file manually

        Args:
            input_file (str): Path to text file (.txt) or audio file (.wav, .mp3, etc.)
        """
        try:
            # Check if it's an audio file
            file_ext = os.path.splitext(input_file)[1].lower()
            is_audio = file_ext in AUDIO_EXTENSIONS

            if is_audio:
                print(f"🎤 Processing audio file: {input_file}")
                print("=" * 60)

                # Lazy-load transcriber
                if self.transcriber is None:
                    print("\n🔄 Loading Whisper transcription model...")
                    self.transcriber = AudioTranscriber(model_size="base")

                # Transcribe audio to text
                print(f"\n📝 Transcribing audio...")
                result = self.transcriber.transcribe(input_file)
                transcript = result['text']
                print(f"✅ Transcription complete ({len(transcript)} characters)")
                print(f"   Language detected: {result['language']}\n")

                # Show preview of transcript
                print("📄 Transcript preview:")
                print("-" * 40)
                preview = transcript[:500] + "..." if len(transcript) > 500 else transcript
                print(preview)
                print("-" * 40 + "\n")
            else:
                print(f"📂 Loading transcript from {input_file}...")
                with open(input_file, 'r') as f:
                    transcript = f.read()
                print(f"✅ Loaded {len(transcript)} characters\n")

            # Ask for prospect email
            prospect_email = input("Enter prospect email (or press Enter to skip): ").strip()
            if not prospect_email:
                prospect_email = None

            # Process the call
            self.process_call(transcript, prospect_email)

            print("\n✨ Done! Check Outreach and Salesforce for updates.")

        except FileNotFoundError:
            print(f"❌ File not found: {input_file}")
            print("💡 Make sure you're in the right directory")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def run_automatic(self):
        """
        Run continuously, checking Orum for new transcripts
        """
        
        print("🤖 Starting automatic mode...")
        print(f"⏱️  Checking for new calls every {self.check_interval} minutes")
        print("⌨️  Press Ctrl+C to stop\n")
        
        try:
            while True:
                print(f"🔍 Checking for new transcripts... [{datetime.now().strftime('%H:%M:%S')}]")
                
                # Get recent transcripts
                transcripts = self.orum.get_recent_transcripts(minutes=self.check_interval)
                
                if transcripts:
                    print(f"✅ Found {len(transcripts)} new calls to process\n")
                    
                    for t in transcripts:
                        # Extract transcript data
                        transcript_text = t.get('transcript', '')
                        prospect_email = t.get('prospect_email', None)
                        
                        # Process it
                        self.process_call(transcript_text, prospect_email)
                        
                        # Small delay between calls
                        time.sleep(2)
                else:
                    print("   No new calls")
                
                # Wait before checking again
                print(f"\n⏸️  Waiting {self.check_interval} minutes...\n")
                time.sleep(self.check_interval * 60)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping automation...")
            print("✅ All done!")


def main():
    """Main entry point"""
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='SDR Automation - Automatically process call transcripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a text transcript:
    python main.py --manual transcript.txt

  Process an audio file (auto-transcribes with Whisper):
    python main.py --manual call_recording.wav

  Run continuously (check Orum every 5 minutes):
    python main.py --auto

Supported audio formats: .wav, .mp3, .m4a, .flac, .ogg, .webm
        """
    )
    
    parser.add_argument(
        '--manual',
        type=str,
        metavar='FILE',
        help='Process a transcript (.txt) or audio file (.wav, .mp3, etc.)'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run continuously, checking Orum for new transcripts'
    )
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = SDRAutomation()
    
    # Run in the appropriate mode
    if args.manual:
        automation.run_manual(args.manual)
    elif args.auto:
        automation.run_automatic()
    else:
        print("❌ Please specify either --manual or --auto mode")
        print("💡 Run 'python main.py --help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
