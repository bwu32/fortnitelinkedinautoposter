# 🎮 Fortnite Victory Royale LinkedIn Auto-Poster

Turn your Fortnite wins into professional LinkedIn content. Automatically detect Victory Royales and generate hilarious LinkedIn posts with AI.

## ✨ Features

- **Automatic Victory Detection**: Hybrid visual + OCR detection for Fortnite Victory Royale screens
- **AI-Powered Post Generation**: 6 different LinkedIn personality modes (Business Bro, Toxic Positivity, Humble Brag, etc.)
- **Smart Automation**: Semi-auto (you click Post) or Full-auto (completely automated) modes
- **Image Upload**: Automatically attaches your victory screenshot to the post
- **Anti-Spam Protection**: 60-second cooldown + screen change detection prevents duplicate posts
- **Session Management**: Stays logged into LinkedIn between uses

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Google Chrome** browser installed
- **OpenAI API Key** (for GPT-4o-mini post generation)
- **LinkedIn Account** (obviously)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/bwu32/fortnitelinkedinautoposter.git
cd fortnitelinkedinautoposter
```

### Step 2: Install Python Dependencies

Copy and paste this command:

```bash
pip install opencv-python pyautogui pillow numpy pywin32 win10toast easyocr selenium openai
```

**Note**: The first run of EasyOCR will download ~500MB of language models. This is normal and only happens once.

### Step 3: Download ChromeDriver

1. Check your Chrome version:
   - Open Chrome
   - Go to `chrome://version/`
   - Note the version number (e.g., 142.0.7444.176)

2. Download matching ChromeDriver:
   - Visit https://googlechromelabs.github.io/chrome-for-testing/
   - Download the version that matches your Chrome
   - Extract `chromedriver.exe` to the same folder as the scripts

### Step 4: Set Up OpenAI API Key

Get your API key from https://platform.openai.com/api-keys

**Windows (PowerShell) - Temporary:**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Windows - Permanent:**
1. Search "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: Your API key
7. Click OK

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Add to `~/.bashrc` or `~/.zshrc` to make permanent.

## ⚙️ Configuration

### First Run - Set Up Preferences

Run the detector for the first time:

```bash
python victory_detector.py
```

When prompted, configure your preferences:

1. **Configure preferences?** → Type `y`
2. **Generate LinkedIn post immediately after win?** → `y` (recommended)
3. **Request extra details after each win?** → `n` (unless you want to manually enter kills/mode)
4. **Save wins for batch review later?** → `n` (not implemented yet)
5. **Choose personality mode (1-6):**
   - 1: Business Bro (corporate jargon)
   - 2: Toxic Positivity (motivational overload)
   - 3: Fake Story (grandfather wisdom)
   - 4: Humble Brag (blessed and grateful)
   - 5: Corporate Jargon (pure buzzwords)
   - 6: Self-Aware (ironic shitposting)
6. **LinkedIn automation level (1/2/3):**
   - 1: Full Auto ⚠️ (violates LinkedIn ToS - posts automatically)
   - 2: Semi-Auto ✅ (recommended - you click Post)
   - 3: Manual (just generates text)

### LinkedIn Login

The first time you run the poster, it will open Chrome and ask you to log in manually:

```bash
python linkedin_poster.py
```

- Log in to LinkedIn when the browser opens
- Your session will be saved for future use
- You won't need to log in again unless you clear the `chrome_linkedin_profile` folder

## 🎯 Usage

### Test Mode (Recommended First)

Test with a victory screenshot before going live:

```bash
python victory_detector.py
```

1. Choose test mode: `y`
2. Open a Fortnite victory screenshot full-screen in a browser
3. Press Enter
4. Watch it detect, generate, and post!

### Live Detection Mode

For actual gameplay:

```bash
python victory_detector.py
```

1. Skip test mode: `n`
2. **Minimize the PowerShell window** (don't close it!)
3. Play Fortnite
4. When you win, it automatically:
   - Screenshots the victory
   - Generates a LinkedIn post
   - Opens LinkedIn and fills everything in
   - Waits for you to click "Post" (semi-auto) or posts automatically (full-auto)

### Stopping Detection

Press `Ctrl+C` in the PowerShell window to stop.

## 📁 File Structure

After setup, your folder should look like:

```
fortnite-linkedin-autoposter/
├── victory_detector.py          # Main detection script
├── linkedin_poster.py            # LinkedIn automation
├── llm_post_generator.py         # AI post generation
├── chromedriver.exe              # Chrome automation driver
├── detector_config.txt           # Your preferences (auto-generated)
├── victory_screenshots/          # Saved victory screenshots (auto-generated)
└── chrome_linkedin_profile/      # LinkedIn session data (auto-generated)
```

## 💰 Cost Estimates

Using **gpt-4o-mini** (recommended):
- ~$0.0005 per post (half a cent)
- $10 = ~20,000 posts
- Even at 10 wins/day, your $10 will last ~5 years

## ⚠️ Important Notes

### LinkedIn Terms of Service

- **Semi-Auto Mode**: ✅ Safe - you manually click Post
- **Full-Auto Mode**: ⚠️ Violates LinkedIn ToS - use at your own risk

We recommend Semi-Auto mode to avoid potential account issues.

### Detection Requirements

- Victory screen must be **visible and large** on your screen
- Works best with Fortnite in fullscreen or borderless window
- May have false positives if not fine-tuned for your setup

### Known Issues

- First EasyOCR run takes 30+ seconds (downloading models)
- ChromeDriver must match your Chrome version exactly
- Windows file picker dialog briefly appears during image upload (automatically closed)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install opencv-python pyautogui pillow numpy pywin32 win10toast easyocr selenium openai
```
Restart your terminal after installing.

### ChromeDriver version mismatch
Download ChromeDriver that exactly matches your Chrome version from https://googlechromelabs.github.io/chrome-for-testing/

### LinkedIn won't stay logged in
Don't delete the `chrome_linkedin_profile` folder - this stores your session.

### Victory not detected in test
- Make the victory screenshot **bigger** on your screen
- Ensure the "VICTORY ROYALE" text is clearly visible
- Try with different victory screenshots

### OpenAI API errors
Check that your API key is set correctly:
```bash
echo $env:OPENAI_API_KEY  # Windows PowerShell
echo $OPENAI_API_KEY      # Linux/Mac
```

### Detection too slow
The first run downloads OCR models (~500MB). After that, detection is fast.
Consider using a GPU for faster OCR (set `gpu=True` in `victory_detector.py`).

## 🎨 Customization

### Change the Rickroll Link

Edit `llm_post_generator.py`, line ~150:

```python
post_text += "\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Change this URL
```

### Adjust Detection Sensitivity

Edit `victory_detector.py`, line ~115:

```python
self.min_area = 5000  # Increase for fewer false positives, decrease for better detection
```

### Change Personality Mode

Re-run configuration:
```bash
python victory_detector.py
```
Choose `y` when asked to configure preferences.

Or manually edit `detector_config.txt`.

## 🤝 Contributing

Pull requests welcome! This is a meme project but we maintain quality memes.

## 📜 License

MIT License - do whatever you want with it. If you get banned from LinkedIn, that's on you.

## 🙏 Credits

- Built with Claude (Anthropic)
- Powered by GPT-4o-mini (OpenAI)
- Selenium for LinkedIn automation
- EasyOCR for text detection
- Your Fortnite skills (or lack thereof)

---

**Disclaimer**: This tool is for entertainment purposes. Using automation on LinkedIn may violate their Terms of Service. The authors are not responsible for any account issues, job losses, or professional embarrassment resulting from automated Fortnite victory posts.

Remember: Just because you *can* automate LinkedIn posts about Fortnite wins doesn't mean you *should*. But where's the fun in that? 🎮💼
