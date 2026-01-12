# Quick Start Guide - 5 Minutes to First Test

## What You're About to Do
You're going to test the automation with a sample call transcript to see it work!

---

## Step 1: Open Terminal/Command Prompt (1 minute)

### On Mac:
1. Press `Command + Space`
2. Type "terminal"
3. Press Enter

### On Windows:
1. Press `Windows key`
2. Type "command prompt"
3. Press Enter

You should see a black or white window with text. This is where you'll type commands.

---

## Step 2: Navigate to the Project Folder (2 minutes)

In the Terminal/Command Prompt window, you need to go to where you saved these files.

### Easy Method (Drag and Drop):
1. Type `cd ` (that's c-d-space)
2. Find the `sdr-automation` folder on your computer
3. **Drag the folder** into the Terminal window
4. Press Enter

### Manual Method:
If your folder is on your Desktop:
```bash
cd Desktop/sdr-automation
```

If it's in Documents:
```bash
cd Documents/sdr-automation
```

**How to know it worked:**
Type `ls` (Mac) or `dir` (Windows) and press Enter. You should see files like:
- main.py
- analyzer.py
- README.md
- etc.

---

## Step 3: Install Python Packages (2 minutes)

Copy this command, paste it into Terminal, and press Enter:

```bash
pip install -r requirements.txt
```

You'll see a bunch of text scroll by. Wait for it to finish (takes 1-2 minutes).

**What if I get an error?**
- Try: `pip3 install -r requirements.txt`
- Still not working? You might need to install Python first (see full README)

---

## Step 4: Set Up Your Configuration (5 minutes)

1. In the `sdr-automation` folder, find the file `.env.example`
2. Make a copy of it
3. Rename the copy to `.env` (remove the `.example` part)
4. Open `.env` with any text editor (Notepad, TextEdit, etc.)
5. Fill in AT LEAST these required fields:

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
YOUR_NAME=Your Name
YOUR_EMAIL=your@email.com
YOUR_CALENDAR_LINK=https://calendly.com/yourname
```

Don't have the other API keys yet? That's okay! You can test the analysis part without them.

6. Save the file

---

## Step 5: Test the Setup (30 seconds)

In Terminal, type this and press Enter:

```bash
python test_setup.py
```

You should see green checkmarks (✅) for things that are working.

**What if I see red X's (❌)?**
- Read the error message - it tells you what's missing
- Usually it's an API key in the `.env` file
- Check you saved the file correctly

---

## Step 6: Run Your First Test! (1 minute)

Now for the fun part! We'll analyze the sample call that's included.

Type this and press Enter:

```bash
python main.py --manual sample_call.txt
```

**What should happen:**
You'll see the system:
1. 📞 Analyze the conversation
2. 🔥 Decide the outcome (this sample is a DEAD_END)
3. 📝 Explain the reasoning
4. ✅ Show what action it would take

---

## Step 7: Try With Your Own Call (Optional)

1. Copy a real call transcript from Orum
2. Save it as a text file (e.g., `my_call.txt`) in the `sdr-automation` folder
3. Run:
   ```bash
   python main.py --manual my_call.txt
   ```
4. When asked for email, type the prospect's email (or just press Enter)

---

## Common Issues & Fixes

### "python: command not found"
**Fix:** Try `python3` instead of `python`

### "No module named 'anthropic'"
**Fix:** Run `pip install -r requirements.txt` again

### "Invalid API Key"
**Fix:** Check your `.env` file - make sure you copied the full API key

### "Permission denied"
**Fix:** Try `sudo pip install -r requirements.txt` (you'll need to enter your password)

### Terminal shows weird characters
**Fix:** Close and reopen Terminal

---

## What's Next?

Once the test works:

### To use it for real calls:
1. Get your API keys from Outreach, Salesforce, Orum
2. Add them to your `.env` file
3. Run: `python main.py --auto`
4. It will check for new calls automatically!

### To customize it:
1. Edit `email_templates.py` to change email wording
2. Edit `analyzer.py` to adjust decision logic
3. Edit `.env` to change timing, sequences, etc.

---

## Quick Reference

```bash
# Navigate to project
cd path/to/sdr-automation

# Test setup
python test_setup.py

# Process one call
python main.py --manual transcript.txt

# Run automatically
python main.py --auto

# Stop the program
Press Ctrl+C
```

---

## Still Stuck?

### Common Questions:

**Q: Where do I type these commands?**
A: In Terminal (Mac) or Command Prompt (Windows)

**Q: How do I know if Python is installed?**
A: Type `python --version` and press Enter. Should show "Python 3.x.x"

**Q: What's an API key?**
A: It's like a password that lets the program access other services

**Q: Do I need all the API keys to test?**
A: No! You can test the conversation analysis with just the Anthropic key

**Q: This is confusing!**
A: That's okay! Take it one step at a time. Start with just Step 6.

---

Remember: You don't need to understand how the code works, you just need to follow these steps! 

Like following a recipe - you don't need to understand chemistry to bake a cake. 🍰
