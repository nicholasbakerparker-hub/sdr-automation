# SDR Automation Tool - Complete Setup Guide
## For Complete Beginners (No Coding Experience Required!)

This tool automatically analyzes your Orum call transcripts, decides if prospects are interested, and creates personalized follow-up emails in Outreach.

---

## 🎯 What This Does

After every call:
1. **Reads the transcript** from Orum
2. **Analyzes the conversation** (Was it interested? Dead end? Warm?)
3. **If interested:** Creates personalized email in Outreach with calendar link
4. **If dead end:** Updates Salesforce, removes from sequences
5. **All automatic** - saves you hours daily

---

## 📋 What You'll Need Before Starting

### Accounts & Access
- [ ] Orum account with API access
- [ ] Outreach account with API access
- [ ] Salesforce account with API access
- [ ] Google Calendar (for meeting links)
- [ ] A computer (Windows, Mac, or Linux)

### API Keys You'll Need to Get
Don't worry - I'll show you exactly where to find each one!

1. **Orum API Key** - Contact your Orum admin or support
2. **Outreach API Key** - Get from Outreach settings
3. **Salesforce Credentials** - Username, password, security token
4. **Anthropic API Key** (for Claude) - Sign up at console.anthropic.com
5. **Google Calendar API** - We'll set this up together

---

## 🚀 Step 1: Install Python (5 minutes)

Python is the language this tool is written in. Think of it like installing Microsoft Word to open .doc files.

### For Windows:
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Run the installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH"
5. Click "Install Now"
6. Wait for it to finish
7. Click "Close"

### For Mac:
1. Open "Terminal" (press Cmd+Space, type "terminal", press Enter)
2. Copy and paste this, then press Enter:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. After that finishes, copy and paste this:
   ```
   brew install python
   ```
4. Wait for it to finish

### Test if it worked:
1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type: `python --version`
3. Press Enter
4. You should see something like "Python 3.12.1"

---

## 🚀 Step 2: Download This Project (2 minutes)

### Option A: If you received these files as a folder
1. Move the folder to your Desktop or Documents
2. Remember where you put it!

### Option B: If you have a GitHub link
1. Click the green "Code" button
2. Click "Download ZIP"
3. Unzip the folder
4. Move it to your Desktop

---

## 🚀 Step 3: Install Required Packages (3 minutes)

Think of this like installing plugins. The code needs some extra tools to work.

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Navigate to the project folder:
   - Type: `cd ` (with a space after cd)
   - Drag the project folder into the Terminal window
   - Press Enter
3. Copy and paste this command:
   ```
   pip install -r requirements.txt
   ```
4. Press Enter and wait (takes 1-2 minutes)

---

## 🚀 Step 4: Get Your API Keys (15 minutes)

This is like getting keys to different buildings. Each service needs its own key.

### 1. Anthropic (Claude) API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Click "API Keys" in the sidebar
4. Click "Create Key"
5. Name it "SDR Automation"
6. Copy the key (starts with "sk-ant-")
7. **SAVE THIS** - you won't see it again!

### 2. Outreach API Key
1. Log into Outreach
2. Click your profile picture (top right)
3. Go to Settings → API
4. Click "Generate New Token"
5. Copy the token
6. Save it somewhere safe

### 3. Salesforce Credentials
You need three things:
- Your Salesforce username (your email)
- Your Salesforce password
- Your security token

**To get your security token:**
1. Log into Salesforce
2. Click your profile picture → Settings
3. On the left, search for "Reset My Security Token"
4. Click "Reset Security Token"
5. Check your email - they'll send you the token
6. Save it!

### 4. Orum API Key
1. Contact your Orum account manager or support
2. Ask for "API access for transcript retrieval"
3. They'll provide you with credentials

### 5. Google Calendar API (We'll do this in Step 6)

---

## 🚀 Step 5: Configure Your Settings (10 minutes)

Now we'll tell the tool where to find your accounts.

1. In the project folder, find the file named `.env.example`
2. Make a copy of it
3. Rename the copy to just `.env` (no ".example")
4. Open `.env` with any text editor (Notepad, TextEdit, etc.)
5. Fill in your information:

```
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Outreach API
OUTREACH_API_KEY=your-outreach-key-here

# Salesforce
SALESFORCE_USERNAME=your.email@company.com
SALESFORCE_PASSWORD=your-password-here
SALESFORCE_SECURITY_TOKEN=your-token-here

# Orum API
ORUM_API_KEY=your-orum-key-here
ORUM_API_URL=https://api.orum.com/v1

# Your Details
YOUR_CALENDAR_LINK=https://calendly.com/yourname
YOUR_EMAIL=your.email@company.com
YOUR_NAME=Your Name
```

6. Save the file
7. **IMPORTANT:** Never share this file with anyone - it has your passwords!

---

## 🚀 Step 6: Set Up Google Calendar (10 minutes)

This creates your meeting booking link.

### Option A: Use Calendly (Easier)
1. Go to calendly.com
2. Sign up with your Google account
3. Set your availability
4. Copy your Calendly link
5. Paste it in the `.env` file under `YOUR_CALENDAR_LINK`

### Option B: Use Google Calendar API (More advanced)
I'll walk you through this if you need it - just ask!

---

## 🚀 Step 7: Customize Email Templates (5 minutes)

Make the emails sound like YOU.

1. Open `email_templates.py`
2. You'll see templates like this:

```python
INTERESTED_EMAIL = """
Hi {first_name},

Great speaking with you earlier about {topic}. {personalized_opener}

{custom_content}

Ready to explore this further? Book a time here: {calendar_link}

Best,
{your_name}
"""
```

3. Edit the text to match your style
4. Keep the parts in `{curly_braces}` - those get filled in automatically
5. Save the file

---

## 🎉 Step 8: Run Your First Test! (5 minutes)

Let's make sure everything works!

1. Open Terminal/Command Prompt
2. Navigate to your project folder (like in Step 3)
3. Type:
   ```
   python test_setup.py
   ```
4. Press Enter

**What should happen:**
- You'll see: "✓ Python is working!"
- "✓ All packages installed!"
- "✓ API keys configured!"
- "✓ Ready to go!"

**If you see errors:**
- Read the error message carefully
- It will tell you what's missing
- Usually it's an API key that wasn't added to `.env`

---

## 🚀 Step 9: Process Your First Call (THE EXCITING PART!)

### Manual Mode (Start Here)
This lets you test with a single call transcript.

1. Copy a call transcript from Orum
2. Save it as a text file on your desktop (call it `test_call.txt`)
3. In Terminal, type:
   ```
   python main.py --manual test_call.txt
   ```
4. Press Enter
5. Watch the magic happen!

**What you'll see:**
```
📞 Analyzing call transcript...
✓ Call analyzed: INTERESTED
📧 Generating personalized email...
✓ Email created!
📤 Scheduling in Outreach for tomorrow 9 AM
✓ Done! Email scheduled.
📝 Updated Salesforce
```

### Automatic Mode (Once You're Confident)
This runs continuously and checks Orum for new calls every 5 minutes.

1. In Terminal, type:
   ```
   python main.py --auto
   ```
2. Press Enter
3. Leave it running!
4. It will process calls automatically as they come in

---

## 📊 How to Know It's Working

### Check Outreach:
1. Log into Outreach
2. Go to "Prospects"
3. Search for the person you just called
4. You should see a scheduled email!

### Check Salesforce:
1. Log into Salesforce
2. Find the lead/contact
3. Check the Activity History
4. You should see the call logged with analysis

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError"
- You didn't install the packages
- Go back to Step 3

### "Invalid API Key"
- Check your `.env` file
- Make sure you copied the full key (no spaces)
- Make sure the key hasn't expired

### "Connection Error"
- Check your internet connection
- Some company networks block API calls - try your home WiFi

### "File Not Found"
- Make sure you're in the right folder in Terminal
- Use the `cd` command to navigate

### Still stuck?
Contact me and send:
1. A screenshot of the error
2. Which step you're on
3. What you were trying to do

---

## 🎯 Next Steps & Advanced Features

Once you're comfortable with the basics:

### Run 24/7 on a Cloud Server
- I'll help you set up AWS or Digital Ocean
- Costs about $10-15/month
- Runs even when your computer is off

### Customize the Decision Logic
- Edit `analyzer.py` to adjust what counts as "interested"
- Add your own keywords
- Change email triggers

### Add More Integrations
- Connect to Slack for notifications
- Add SMS follow-ups
- Create Notion logs

---

## 📞 Need Help?

Don't be shy! Everyone gets stuck sometimes.

**Common Questions:**
- "I don't see Terminal/Command Prompt" → Search for it in your apps
- "The commands aren't working" → Make sure you're in the project folder
- "I broke something" → Just re-download the files and start over
- "Can you help me with X?" → Yes! Just ask

---

## 🎓 What You've Built

You now have an AI-powered SDR assistant that:
- ✅ Analyzes every call in seconds
- ✅ Decides the best next action
- ✅ Creates personalized emails
- ✅ Schedules follow-ups automatically  
- ✅ Updates your CRM
- ✅ Saves you 10+ hours per week

**You did that! And you "don't know code" 😉**

---

## 📝 Quick Reference Commands

```bash
# Navigate to project
cd /path/to/sdr-automation

# Run test
python test_setup.py

# Process one call manually
python main.py --manual transcript.txt

# Run automatically (24/7 mode)
python main.py --auto

# Stop the program
Press Ctrl+C
```

---

**Questions? Stuck on a step? Just ask - I'm here to help!**
