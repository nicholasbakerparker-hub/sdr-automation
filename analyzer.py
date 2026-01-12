"""
Conversation Analyzer
This module analyzes sales call transcripts to determine prospect interest level
"""

import re
import requests


class ConversationAnalyzer:
    """
    Analyzes sales call transcripts using Ollama (local AI)
    Determines if prospects are interested, warm, nurture-worthy, or dead ends
    """

    def __init__(self, model="llama3.2", ollama_url="http://localhost:11434"):
        """Initialize the analyzer with Ollama"""
        self.model = model
        self.ollama_url = ollama_url

        # Verify Ollama is running
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama at {self.ollama_url}. Is Ollama running? Error: {e}")
    
    def analyze_call(self, transcript, prospect_name=None):
        """
        Analyze a call transcript and determine the outcome
        
        Args:
            transcript (str): The full call transcript
            prospect_name (str, optional): Name of the prospect for context
            
        Returns:
            dict: Analysis results with decision, reasoning, and next actions
        """
        
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(transcript, prospect_name)
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()

            # Extract the text response
            analysis_text = response.json().get("response", "")
            
            # Parse the response into structured data
            result = self._parse_analysis(analysis_text)
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing call: {str(e)}")
            return {
                'decision': 'ERROR',
                'reasoning': f'Failed to analyze: {str(e)}',
                'confidence': 0,
                'next_action': 'manual_review'
            }
    
    def _build_analysis_prompt(self, transcript, prospect_name):
        """Build the prompt for Claude to analyze the conversation"""
        
        prompt = f"""You are an expert sales call analyzer. Analyze this SDR sales call transcript and determine the outcome.

CRITICAL INSTRUCTIONS:
- Read the ENTIRE conversation before deciding
- Track how the prospect's position evolves throughout the call
- Prioritize statements near the END over the beginning
- Identify if objections were overcome or remained barriers
- Look for commitment language in the final exchanges
- Consider the overall conversation arc, not just keywords

PROSPECT NAME: {prospect_name if prospect_name else 'Unknown'}

CALL TRANSCRIPT:
{transcript}

Please analyze this call and provide your assessment in the following format:

1. INITIAL POSITION: [How did the prospect start the conversation?]

2. OBJECTIONS RAISED: [List any concerns or barriers mentioned]

3. OBJECTIONS ADDRESSED: [Were objections overcome? How?]

4. MIND CHANGES: [Did sentiment shift during the call? From what to what?]

5. FINAL SENTIMENT: [Focus on the last 3-5 exchanges - what's the tone and outcome?]

6. COMMITMENT LEVEL: [Did they commit to any next steps? What exactly?]

7. KEY INDICATORS:
   - Interest signals: [quotes showing interest]
   - Rejection signals: [quotes showing disinterest]
   - Action items: [what they want to happen next]

8. DECISION: Choose ONE of these:
   - INTERESTED: Explicitly wants more info, asked to be contacted, mentioned next steps
   - WARM: Some interest but not ready now, asked questions, engaged but no commitment
   - NURTURE: Future potential mentioned but not now, wrong timing, needs to talk to others
   - DEAD_END: Explicit rejection, wrong contact with no referral, no budget/authority/need

9. CONFIDENCE: [1-10, how certain are you of this decision?]

10. REASONING: [2-3 sentences explaining your decision, focusing on the conversation arc]

11. RECOMMENDED EMAIL TOPICS: [If interested/warm, what should the follow-up email focus on?]

DECISION RULES:
✅ INTERESTED if:
- Asks for information to be sent
- Mentions timeline ("check back in Q2")
- Asks about pricing, implementation, case studies
- Says "let me talk to [decision maker]"
- Provides referral contact
- Books a meeting or asks for next steps

⚠️ WARM if:
- Asks questions but doesn't commit
- Engaged but mentions barriers (budget, timing)
- "Interesting but not right now" without specific timing

📅 NURTURE if:
- "Not now but reach out in [future timeframe]"
- Interested but has clear barrier (contract, freeze)
- Wrong contact but seemed interested in concept

❌ DEAD_END if:
- Explicit rejection: "No," "I'll pass," "Not interested"
- Wrong contact with no referral or interest
- Happy with current solution, no pain points
- Just signed competitor contract
- No budget and no interest in ROI discussion

Remember: The FINAL outcome matters most. Someone who starts skeptical but ends interested = INTERESTED.
Someone who seems polite but ends with "No thanks" = DEAD_END."""

        return prompt
    
    def _parse_analysis(self, analysis_text):
        """
        Parse Claude's response into structured data
        
        Args:
            analysis_text (str): The raw text response from Claude
            
        Returns:
            dict: Structured analysis results
        """
        
        # Initialize result dictionary
        result = {
            'decision': 'UNKNOWN',
            'confidence': 5,
            'reasoning': '',
            'initial_position': '',
            'objections': [],
            'final_sentiment': '',
            'commitment_level': '',
            'next_action': '',
            'email_topics': [],
            'raw_analysis': analysis_text
        }
        
        # Parse the decision (case-insensitive, flexible matching)
        analysis_upper = analysis_text.upper()

        # Look for decision patterns
        decision_match = re.search(r'DECISION[:\s]+(\w+)', analysis_upper)
        if decision_match:
            decision_value = decision_match.group(1)
            if 'INTERESTED' in decision_value:
                result['decision'] = 'INTERESTED'
                result['next_action'] = 'send_email'
            elif 'WARM' in decision_value:
                result['decision'] = 'WARM'
                result['next_action'] = 'send_email'
            elif 'NURTURE' in decision_value:
                result['decision'] = 'NURTURE'
                result['next_action'] = 'add_to_nurture_sequence'
            elif 'DEAD' in decision_value:
                result['decision'] = 'DEAD_END'
                result['next_action'] = 'mark_disqualified'
        
        # Parse confidence (look for "CONFIDENCE: X" pattern)
        try:
            if 'CONFIDENCE:' in analysis_text:
                confidence_section = analysis_text.split('CONFIDENCE:')[1].split('\n')[0]
                # Extract first number found
                confidence_match = re.search(r'\d+', confidence_section)
                if confidence_match:
                    result['confidence'] = int(confidence_match.group())
        except:
            result['confidence'] = 5  # Default to medium confidence
        
        # Extract reasoning
        try:
            if 'REASONING:' in analysis_text:
                reasoning_section = analysis_text.split('REASONING:')[1].split('\n\n')[0]
                result['reasoning'] = reasoning_section.strip()
        except:
            result['reasoning'] = "See full analysis for details"
        
        # Extract email topics (if interested/warm)
        if result['decision'] in ['INTERESTED', 'WARM']:
            try:
                if 'RECOMMENDED EMAIL TOPICS:' in analysis_text:
                    topics_section = analysis_text.split('RECOMMENDED EMAIL TOPICS:')[1].split('\n\n')[0]
                    result['email_topics'] = [t.strip('- ').strip() for t in topics_section.split('\n') if t.strip()]
            except:
                result['email_topics'] = ['Follow up on conversation']
        
        return result
    
    def get_decision_emoji(self, decision):
        """Get a friendly emoji for each decision type"""
        emojis = {
            'INTERESTED': '🔥',
            'WARM': '👍',
            'NURTURE': '📅',
            'DEAD_END': '❌',
            'ERROR': '⚠️',
            'UNKNOWN': '❓'
        }
        return emojis.get(decision, '❓')


# Example usage (for testing)
if __name__ == "__main__":
    # This runs if you execute this file directly (for testing)
    print("Testing Conversation Analyzer...")
    
    # Sample transcript
    test_transcript = """
Dan Lauder: Hello. This is Dan.
Nick Parker: Hey, Dan. My name is Nick from Pathify.
Dan Lauder: Sure. Go ahead.
Nick Parker: We help schools consolidate their tech stack and save about 40%.
Dan Lauder: When you say down from 28 to 5, what does that mean?
Nick Parker: Student-facing systems. We integrate with Canvas and other tools.
Dan Lauder: I just handle the LMS. That's not really my area.
Nick Parker: I understand. Would you like to take a look anyway?
Dan Lauder: No. I'll pass on it.
Nick Parker: No problem. Thanks for your time!
"""
    
    try:
        analyzer = ConversationAnalyzer()
        result = analyzer.analyze_call(test_transcript, "Dan Lauder")
        
        print(f"\n{analyzer.get_decision_emoji(result['decision'])} DECISION: {result['decision']}")
        print(f"💯 CONFIDENCE: {result['confidence']}/10")
        print(f"📝 REASONING: {result['reasoning']}")
        print(f"➡️  NEXT ACTION: {result['next_action']}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("Make sure Ollama is running (open the Ollama app)!")
