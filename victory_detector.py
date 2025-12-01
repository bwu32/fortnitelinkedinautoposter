import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
import os
import threading
import easyocr
from llm_post_generator import LinkedInPostGenerator
from linkedin_poster import post_victory_full_auto, post_victory_semi_auto

class VictoryDetector:
    def __init__(self):
        self.running = False
        self.screenshot_folder = "victory_screenshots"
        self.config_file = "detector_config.txt"
        
        # Detection state
        self.last_detection_time = 0
        self.last_screenshot = None
        self.cooldown_active = False
        self.waiting_for_screen_change = False
        
        # Create screenshots folder
        if not os.path.exists(self.screenshot_folder):
            os.makedirs(self.screenshot_folder)
        
        # Victory Royale color ranges (HSV) - updated based on screenshots
        # Blue victory banner (from screenshots 1 & 2)
        self.blue_lower = np.array([90, 100, 100])
        self.blue_upper = np.array([130, 255, 255])
        
        # Orange/Gold victory banner (from screenshots 2 & 3)
        self.orange_lower = np.array([10, 100, 100])
        self.orange_upper = np.array([25, 255, 255])
        
        # White text detection (for "VICTORY ROYALE" text)
        self.white_lower = np.array([0, 0, 200])
        self.white_upper = np.array([180, 30, 255])
        
        # Minimum area for detection (adjust based on screen size)
        self.min_area = 5000
        
        # Initialize OCR reader (loads once at startup)
        print("🔤 Loading OCR model...")
        self.ocr_reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if you have CUDA
        
        # Initialize LLM post generator
        try:
            print("🤖 Initializing LLM post generator...")
            self.post_generator = LinkedInPostGenerator()
            print("✅ LLM ready!")
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            self.post_generator = None
        
        # Load preferences
        self.preferences = self.load_preferences()
        
        print("Victory Royale Detector initialized!")
        print(f"Screenshots will be saved to: {self.screenshot_folder}")
        print(f"Current preferences: {self.preferences}")
    
    def load_preferences(self):
        """Load user preferences from config file"""
        default_prefs = {
            'generate_immediately': True,
            'request_extra_details': False,
            'review_later': False,
            'linkedin_automation': 'semi-auto',  # 'full-auto', 'semi-auto', or 'manual'
            'personality_mode': 'business_bro'  # Default personality
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    prefs = {}
                    for line in f:
                        key, value = line.strip().split('=')
                        if key in ['linkedin_automation', 'personality_mode']:
                            prefs[key] = value
                        else:
                            prefs[key] = value.lower() == 'true'
                    return prefs
        except:
            pass
        
        return default_prefs
    
    def save_preferences(self, prefs):
        """Save user preferences to config file"""
        with open(self.config_file, 'w') as f:
            for key, value in prefs.items():
                f.write(f"{key}={value}\n")
    
    def setup_preferences(self):
        """Interactive preference setup"""
        print("\n" + "="*50)
        print("🎯 VICTORY DETECTION PREFERENCES")
        print("="*50)
        
        prefs = {}
        
        print("\n📝 LinkedIn Post Generation:")
        prefs['generate_immediately'] = input("  ✓ Generate LinkedIn post immediately after win? (y/n): ").lower() == 'y'
        
        print("\n🎮 Extra Details:")
        prefs['request_extra_details'] = input("  ✓ Request extra details after each win? (kills, mode, etc.) (y/n): ").lower() == 'y'
        
        print("\n📊 Review Mode:")
        prefs['review_later'] = input("  ✓ Save wins for batch review later? (y/n): ").lower() == 'y'
        
        print("\n🎭 Personality Mode:")
        print("  1. Business Bro (Serious corporate jargon)")
        print("  2. Toxic Positivity (Motivational overload)")
        print("  3. Fake Story (Unrelated grandfather stories)")
        print("  4. Humble Brag (Blessed and grateful)")
        print("  5. Corporate Jargon (Pure buzzwords)")
        print("  6. Self-Aware (Ironic shitposting)")
        personality_choice = input("  Choose personality (1-6): ").strip()
        
        personality_map = {
            '1': 'business_bro',
            '2': 'toxic_positivity',
            '3': 'fake_story',
            '4': 'humble_brag',
            '5': 'corporate_jargon',
            '6': 'self_aware'
        }
        prefs['personality_mode'] = personality_map.get(personality_choice, 'business_bro')
        
        print("\n🤖 LinkedIn Automation Level:")
        print("  1. Full Auto (⚠️ May violate LinkedIn ToS - posts automatically)")
        print("  2. Semi-Auto (Opens LinkedIn, fills post, you click 'Post')")
        print("  3. Manual (Just generates text + notification)")
        automation_choice = input("  Choose (1/2/3): ").strip()
        
        automation_map = {
            '1': 'full-auto',
            '2': 'semi-auto', 
            '3': 'manual'
        }
        prefs['linkedin_automation'] = automation_map.get(automation_choice, 'semi-auto')
        
        print(f"\n✅ Preferences saved!")
        print(f"   Generate immediately: {prefs['generate_immediately']}")
        print(f"   Request extra details: {prefs['request_extra_details']}")
        print(f"   Review later: {prefs['review_later']}")
        print(f"   Personality: {prefs['personality_mode']}")
        print(f"   LinkedIn automation: {prefs['linkedin_automation']}")
        
        if prefs['linkedin_automation'] == 'full-auto':
            print("\n⚠️  WARNING: Full automation may violate LinkedIn's Terms of Service!")
            print("   Use at your own risk.")
        
        self.save_preferences(prefs)
        self.preferences = prefs
        return prefs
    
    def screen_changed_significantly(self, current_screen):
        """Check if screen has changed significantly from last victory detection"""
        if self.last_screenshot is None:
            return True
            
        # Compare current screen to last detection screenshot
        # Convert both to grayscale for comparison
        current_gray = cv2.cvtColor(current_screen, cv2.COLOR_BGR2GRAY)
        last_gray = cv2.cvtColor(self.last_screenshot, cv2.COLOR_BGR2GRAY)
        
        # Resize both to same size for comparison
        height, width = min(current_gray.shape[0], last_gray.shape[0]), min(current_gray.shape[1], last_gray.shape[1])
        current_resized = cv2.resize(current_gray, (width, height))
        last_resized = cv2.resize(last_gray, (width, height))
        
        # Calculate difference
        diff = cv2.absdiff(current_resized, last_resized)
        diff_percentage = (np.sum(diff > 30) / diff.size) * 100
        
        # Screen changed if >15% of pixels are significantly different
        return diff_percentage > 15.0

    def detect_victory_with_ocr(self, image):
        """Hybrid detection: Visual banner + OCR text verification"""
        
        # Step 1: Visual banner detection (existing logic)
        visual_detected, color_mask = self.detect_victory_colors(image)
        
        if not visual_detected:
            return False, color_mask, "No visual banner detected"
        
        # Step 2: OCR verification in potential banner areas
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Find potential banner regions from color detection
        blue_mask = cv2.inRange(hsv, np.array([100, 120, 120]), np.array([120, 255, 255]))
        orange_mask = cv2.inRange(hsv, np.array([12, 120, 120]), np.array([22, 255, 255]))
        combined_mask = cv2.bitwise_or(blue_mask, orange_mask)
        
        # Get bounding boxes of potential banners
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        img_height, img_width = image.shape[:2]
        victory_text_found = False
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                rect = cv2.boundingRect(contour)
                x, y, w, h = rect
                
                # Expand search area around banner for text
                search_x1 = max(0, x - 20)
                search_y1 = max(0, y - 20)
                search_x2 = min(img_width, x + w + 20)
                search_y2 = min(img_height, y + h + 20)
                
                # Extract region of interest
                roi = image[search_y1:search_y2, search_x1:search_x2]
                
                if roi.size > 0:
                    try:
                        # Run OCR on the banner region
                        results = self.ocr_reader.readtext(roi, detail=1, paragraph=False)
                        
                        detected_text = ""
                        for (bbox, text, confidence) in results:
                            if confidence > 0.5:  # Only consider confident detections
                                detected_text += text.upper() + " "
                        
                        print(f"🔤 OCR detected: '{detected_text.strip()}' (confidence threshold: 0.5)")
                        
                        # Check for victory royale text patterns
                        victory_patterns = [
                            "VICTORY ROYALE",
                            "VICTORY",
                            "ROYALE" 
                        ]
                        
                        # Must contain both VICTORY and ROYALE (can be separate)
                        has_victory = any("VICTORY" in detected_text for pattern in victory_patterns if "VICTORY" in pattern)
                        has_royale = any("ROYALE" in detected_text for pattern in victory_patterns if "ROYALE" in pattern)
                        
                        if has_victory and has_royale:
                            victory_text_found = True
                            print("✅ OCR confirmed: Found 'VICTORY' and 'ROYALE' text!")
                            break
                        elif "VICTORY ROYALE" in detected_text:
                            victory_text_found = True
                            print("✅ OCR confirmed: Found 'VICTORY ROYALE' text!")
                            break
                            
                    except Exception as e:
                        print(f"⚠️ OCR error in region: {e}")
                        continue
        
        if victory_text_found:
            return True, color_mask, "Visual banner + OCR text confirmed"
        else:
            return False, color_mask, "Visual banner found but no 'VICTORY ROYALE' text detected"
    
    def detect_victory_colors(self, image):
        """Detect victory royale banner colors and patterns in image - STRICT MODE"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # More restrictive color ranges to avoid false positives
        # Blue victory banner - tighter range
        blue_mask = cv2.inRange(hsv, np.array([100, 120, 120]), np.array([120, 255, 255]))
        
        # Orange victory banner - tighter range  
        orange_mask = cv2.inRange(hsv, np.array([12, 120, 120]), np.array([22, 255, 255]))
        
        # White text detection - very specific
        white_mask = cv2.inRange(hsv, np.array([0, 0, 220]), np.array([180, 25, 255]))
        
        # Combine color masks
        color_mask = cv2.bitwise_or(blue_mask, orange_mask)
        
        # Much more aggressive morphological operations to find banner shapes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 8))
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        victory_score = 0
        banner_found = False
        
        # Much stricter banner detection
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area * 2:  # Double the minimum area requirement
                
                # Check if contour is banner-shaped (wide rectangle)
                rect = cv2.boundingRect(contour)
                width, height = rect[2], rect[3]
                aspect_ratio = width / height if height > 0 else 0
                
                # Victory banners must be very specifically shaped
                if 3.0 < aspect_ratio < 5.5:
                    
                    # Check banner position (victory banners appear in upper-middle area)
                    img_height, img_width = image.shape[:2]
                    banner_y_center = rect[1] + rect[3]/2
                    banner_x_center = rect[0] + rect[2]/2
                    
                    # Banner should be in upper 40% of screen and reasonably centered
                    if (banner_y_center < img_height * 0.4 and 
                        img_width * 0.2 < banner_x_center < img_width * 0.8):
                        
                        banner_found = True
                        victory_score += 2
                        
                        # Look for "VICTORY ROYALE" text in and around the banner
                        x, y, w, h = rect
                        text_search_area = white_mask[max(0, y-20):min(img_height, y+h+20), 
                                                    max(0, x-20):min(img_width, x+w+20)]
                        
                        white_pixels = np.sum(text_search_area > 0)
                        if white_pixels > 2000:  # Substantial white text
                            victory_score += 3
                            
                            # Additional check: look for text that spans most of banner width
                            text_contours, _ = cv2.findContours(text_search_area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            for text_contour in text_contours:
                                text_rect = cv2.boundingRect(text_contour)
                                text_width = text_rect[2]
                                if text_width > w * 0.6:  # Text spans 60% of banner width
                                    victory_score += 2
                                    break
        
        # Much higher threshold - need strong evidence
        is_victory = victory_score >= 4 and banner_found
        
        if victory_score > 0:
            print(f"🔍 Detection score: {victory_score}/7 (need ≥4)")
        
        return is_victory, color_mask
    
    def take_screenshot(self):
        """Capture Fortnite window specifically, fallback to full screen"""
        import win32gui
        import win32ui
        import win32con
        
        # Try to find Fortnite window first
        fortnite_window = None
        fortnite_titles = ["Fortnite", "FortniteClient-Win64-Shipping"]
        
        def enum_windows_callback(hwnd, titles):
            window_title = win32gui.GetWindowText(hwnd)
            for title in titles:
                if title.lower() in window_title.lower() and win32gui.IsWindowVisible(hwnd):
                    titles.append(hwnd)
                    return False
            return True
        
        window_handles = []
        try:
            win32gui.EnumWindows(enum_windows_callback, window_handles)
            if window_handles:
                fortnite_window = window_handles[0]
        except:
            pass
        
        # Capture Fortnite window if found
        if fortnite_window:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(fortnite_window)
                width = right - left
                height = bottom - top
                
                # Get window device context
                hwndDC = win32gui.GetWindowDC(fortnite_window)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                # Create bitmap
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                # Copy window content
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Convert to numpy array
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)
                img = img[...,:3]  # Remove alpha channel
                img = np.ascontiguousarray(img[:, :, ::-1])  # BGR to RGB, then flip
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(fortnite_window, hwndDC)
                
                print("📱 Captured Fortnite window")
                return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
            except Exception as e:
                print(f"⚠️ Failed to capture Fortnite window: {e}")
        
        # Fallback to full screen
        print("🖥️ Capturing full screen (Fortnite window not found)")
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def save_victory_screenshot(self, image):
        """Save victory screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"victory_{timestamp}.png"
        filepath = os.path.join(self.screenshot_folder, filename)
        cv2.imwrite(filepath, image)
        return filepath
    
    def show_victory_notification(self, filepath):
        """Show victory detection notification using Windows toast"""
        try:
            # Try Windows 10/11 toast notification first
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                "🎉 VICTORY ROYALE DETECTED!",
                f"Screenshot saved!\nTime for that LinkedIn post! 💼",
                duration=10,
                threaded=True
            )
        except ImportError:
            # Fallback to simple print notification
            print("=" * 50)
            print("🎉 VICTORY ROYALE DETECTED! 🎉")
            print(f"📸 Screenshot saved: {filepath}")
            print("💼 Time for that LinkedIn post!")
            print("=" * 50)
        except Exception as e:
            # Another fallback
            print(f"🎉 VICTORY ROYALE DETECTED! Screenshot: {filepath}")
            print(f"⚠️ Notification error: {e}")
    
    def start_detection(self):
        """Start continuous screen monitoring with smart cooldown"""
        self.running = True
        print("🎯 Starting Victory Royale detection...")
        print("🎮 Go get those wins!")
        print("⏹️  Press Ctrl+C to stop")
        
        try:
            while self.running:
                current_time = time.time()
                screen = self.take_screenshot()
                
                # Check cooldown status
                if self.cooldown_active:
                    if current_time - self.last_detection_time >= 60:  # 60 second cooldown
                        if self.screen_changed_significantly(screen):
                            print("✅ Screen changed significantly. Detection resumed!")
                            self.cooldown_active = False
                            self.waiting_for_screen_change = False
                        elif not self.waiting_for_screen_change:
                            print("⏳ Cooldown finished. Waiting for screen to change...")
                            self.waiting_for_screen_change = True
                else:
                    # Normal detection - now using hybrid OCR method
                    victory_detected, mask, reason = self.detect_victory_with_ocr(screen)
                    
                    if victory_detected:
                        print(f"🏆 VICTORY ROYALE DETECTED! Reason: {reason}")
                        
                        # Save screenshot and start cooldown
                        filepath = self.save_victory_screenshot(screen)
                        print(f"📸 Screenshot saved: {filepath}")
                        
                        # Store this screenshot for comparison
                        self.last_screenshot = screen.copy()
                        self.last_detection_time = current_time
                        self.cooldown_active = True
                        
                        # Handle based on preferences
                        self.handle_victory_detection(filepath)
                        
                        print("🔒 Detection paused for 60 seconds + screen change...")
                    elif "Visual banner found" in reason:
                        print(f"⚠️ Near miss: {reason}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n🛑 Detection stopped!")
            self.running = False
    
    def handle_victory_detection(self, filepath):
        """Handle victory based on user preferences"""
        extra_details = None
        
        # Request extra details if configured
        if self.preferences['request_extra_details']:
            print("\n🎮 Enter game details (or press Enter to skip):")
            kills = input("  Eliminations: ").strip()
            mode = input("  Game mode (Solos/Duos/Squads/etc): ").strip()
            
            extra_details = {}
            if kills:
                try:
                    extra_details['kills'] = int(kills)
                except:
                    pass
            if mode:
                extra_details['mode'] = mode
            extra_details['placement'] = 1  # Always #1 for Victory Royale!
        
        generated_post = None
        
        # Generate post if configured
        if self.preferences['generate_immediately'] and self.post_generator:
            print("📝 Generating LinkedIn post...")
            personality = self.preferences.get('personality_mode', 'business_bro')
            generated_post = self.post_generator.generate_post(
                personality=personality,
                extra_details=extra_details
            )
            
            if generated_post:
                print("\n" + "="*60)
                print("GENERATED POST:")
                print("="*60)
                print(generated_post)
                print("="*60 + "\n")
                
                # Save post to file
                post_filename = filepath.replace('.png', '_post.txt')
                with open(post_filename, 'w', encoding='utf-8') as f:
                    f.write(generated_post)
                print(f"💾 Post saved to: {post_filename}")
        
        # Handle LinkedIn automation
        automation_mode = self.preferences.get('linkedin_automation', 'manual')
        
        if generated_post and automation_mode != 'manual':
            print(f"\n🤖 LinkedIn automation mode: {automation_mode}")
            
            try:
                if automation_mode == 'full-auto':
                    print("🚀 Posting to LinkedIn automatically...")
                    success = post_victory_full_auto(generated_post, filepath)  # Pass the actual screenshot path!
                    if success:
                        print("✅ Posted to LinkedIn successfully!")
                    else:
                        print("❌ LinkedIn posting failed")
                        
                elif automation_mode == 'semi-auto':
                    print("🚀 Opening LinkedIn for semi-auto posting...")
                    success = post_victory_semi_auto(generated_post, filepath)  # Pass the actual screenshot path!
                    if success:
                        print("✅ Post prepared on LinkedIn!")
                    else:
                        print("❌ LinkedIn automation failed")
                        
            except Exception as e:
                print(f"❌ LinkedIn automation error: {e}")
                print(f"📋 Post text and screenshot saved - you can post manually!")
                print(f"   Screenshot: {filepath}")
                print(f"   Post text: {post_filename}")
        
        elif generated_post and automation_mode == 'manual':
            print(f"\n📋 Manual mode: Post generated and saved!")
            print(f"   Screenshot: {filepath}")
            print(f"   Post text: {post_filename}")
        
        # Show notification
        self.show_victory_notification(filepath)

def main():
    detector = VictoryDetector()
    
    print("=" * 50)
    print("🎉 FORTNITE VICTORY ROYALE DETECTOR 🎉")
    print("=" * 50)
    print()
    
    # Setup preferences first
    setup_prefs = input("Configure preferences? (y/n - default uses current settings): ").lower() == 'y'
    if setup_prefs:
        detector.setup_preferences()
    
    # Test mode option
    test_mode = input("\nWant to test with a victory image first? (y/n): ").lower() == 'y'
    
    if test_mode:
        print("\n🧪 TEST MODE:")
        print("1. Open a Fortnite victory royale image/video in your browser")
        print("2. Make it large on your screen") 
        print("3. Press Enter when ready...")
        input()
        
        # Take test screenshot
        screen = detector.take_screenshot()
        victory_detected, mask, reason = detector.detect_victory_with_ocr(screen)
        
        if victory_detected:
            print(f"✅ Victory detected in test! Reason: {reason}")
            filepath = detector.save_victory_screenshot(screen)
            print(f"📸 Test screenshot saved: {filepath}")
            detector.show_victory_notification(filepath)
        else:
            print(f"❌ No victory detected. Reason: {reason}")
            print("Try adjusting the image size or brightness.")
            
        print("\nReady for live detection? Press Enter...")
        input()
    
    # Start live detection
    detector.start_detection()

if __name__ == "__main__":
    main()