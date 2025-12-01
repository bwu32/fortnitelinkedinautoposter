from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import pyautogui

class LinkedInPoster:
    def __init__(self, headless=False):
        """Initialize LinkedIn poster with Selenium"""
        self.headless = headless
        self.driver = None
        self.session_file = "linkedin_session.txt"
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Add crash prevention options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Add options to appear more like a real user
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User data directory to persist login
        user_data_dir = os.path.join(os.getcwd(), "chrome_linkedin_profile")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def login(self, email=None, password=None):
        """Login to LinkedIn (or check if already logged in)"""
        if not self.driver:
            self.setup_driver()
        
        self.driver.get("https://www.linkedin.com")
        time.sleep(2)
        
        # Check if already logged in
        if "feed" in self.driver.current_url:
            print("✅ Already logged in to LinkedIn!")
            return True
        
        # If credentials provided, attempt login
        if email and password:
            try:
                email_field = self.driver.find_element(By.ID, "session_key")
                password_field = self.driver.find_element(By.ID, "session_password")
                
                email_field.send_keys(email)
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)
                
                time.sleep(3)
                
                if "feed" in self.driver.current_url:
                    print("✅ Login successful!")
                    return True
                else:
                    print("⚠️ Login may require additional verification (2FA, captcha)")
                    return False
                    
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False
        else:
            print("⚠️ Not logged in. Please log in manually or provide credentials.")
            print("   Browser will stay open for manual login...")
            input("   Press Enter after you've logged in manually...")
            return True
    
    def post_to_linkedin(self, text_content, image_path=None, full_auto=True):
        """
        Post to LinkedIn with text and optional image
        
        Args:
            text_content: The post text
            image_path: Path to image to upload (optional)
            full_auto: If True, clicks Post button. If False, leaves it for user to click.
        """
        if not self.driver:
            self.setup_driver()
        
        try:
            # Navigate to LinkedIn feed
            print("📱 Navigating to LinkedIn feed...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Click "Start a post" button - use JavaScript click as fallback
            print("🔍 Looking for 'Start a post' button...")
            
            # Wait for page to fully load
            time.sleep(2)
            
            # Try to find the button with multiple strategies
            clicked = False
            
            # Strategy 1: Direct XPath with text
            try:
                print("   Strategy 1: Looking for button with 'Start a post' text...")
                buttons = self.driver.find_elements(By.XPATH, "//button")
                for button in buttons:
                    if "Start a post" in button.text and button.is_displayed():
                        print(f"   Found button with text: '{button.text}'")
                        # Try regular click first
                        try:
                            button.click()
                            clicked = True
                            print("✅ Clicked 'Start a post' with Strategy 1")
                            break
                        except:
                            # If regular click fails, try JavaScript click
                            self.driver.execute_script("arguments[0].click();", button)
                            clicked = True
                            print("✅ Clicked 'Start a post' with Strategy 1 (JS click)")
                            break
            except Exception as e:
                print(f"   ❌ Strategy 1 failed: {e}")
            
            # Strategy 2: Find by class and text
            if not clicked:
                try:
                    print("   Strategy 2: Looking for share-box area...")
                    share_box = self.driver.find_element(By.XPATH, "//div[contains(@class, 'share-box')]")
                    self.driver.execute_script("arguments[0].click();", share_box)
                    clicked = True
                    print("✅ Clicked share box with Strategy 2")
                except Exception as e:
                    print(f"   ❌ Strategy 2 failed: {e}")
            
            # Strategy 3: Click anywhere in the "Start a post" input-like area
            if not clicked:
                try:
                    print("   Strategy 3: Looking for clickable post input area...")
                    post_input = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Start a post')]")
                    self.driver.execute_script("arguments[0].click();", post_input)
                    clicked = True
                    print("✅ Clicked with Strategy 3")
                except Exception as e:
                    print(f"   ❌ Strategy 3 failed: {e}")
            
            if not clicked:
                print("❌ All strategies failed!")
                print("📸 Taking screenshot and saving page source...")
                self.driver.save_screenshot("debug_cant_find_button.png")
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("   Files saved: debug_cant_find_button.png and debug_page_source.html")
                raise Exception("Could not find or click 'Start a post' button")
            
            print("⏳ Waiting for composer to open...")
            time.sleep(2)
            
            # Find the text editor (contenteditable div)
            print("🔍 Looking for text editor...")
            text_editor = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @role='textbox']"))
            )
            print("✅ Found text editor")
            
            # Enter text content - use JavaScript to avoid Unicode issues
            text_editor.click()
            time.sleep(0.5)
            
            # Split the text to handle the hyperlink separately
            # Check if text has the signature with placeholder for link
            if "Fortnite LinkedIn Auto-Poster" in text_content and "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in text_content:
                # Remove the plain URL and prepare to add as hyperlink
                text_without_url = text_content.replace("\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ", "")
                
                # Use JavaScript to set the text
                escaped_text = text_without_url.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                self.driver.execute_script(f'arguments[0].innerText = "{escaped_text}";', text_editor)
                
                # Now we need to select "Fortnite LinkedIn Auto-Poster" and add hyperlink
                # Use JavaScript to create a hyperlink
                self.driver.execute_script("""
                    var editor = arguments[0];
                    var text = editor.innerText;
                    var linkText = "Fortnite LinkedIn Auto-Poster";
                    var url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
                    
                    // Find the text and replace with anchor tag
                    var newHTML = editor.innerHTML.replace(linkText, '<a href="' + url + '" target="_blank">' + linkText + '</a>');
                    editor.innerHTML = newHTML;
                """, text_editor)
                
            else:
                # Regular text without hyperlink
                escaped_text = text_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                self.driver.execute_script(f'arguments[0].innerText = "{escaped_text}";', text_editor)
            
            # Trigger input event so LinkedIn knows text was added
            self.driver.execute_script("""
                var event = new Event('input', { bubbles: true });
                arguments[0].dispatchEvent(event);
            """, text_editor)
            
            print("✅ Text entered")
            time.sleep(1)
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                print(f"📸 Uploading image: {image_path}")
                
                try:
                    # Look for the photo/media button - it's the image icon in the toolbar
                    print("   Looking for photo upload button...")
                    
                    # Multiple strategies to find the photo button
                    photo_button = None
                    
                    # Strategy 1: Find by icon/image button
                    try:
                        # Look for buttons in the toolbar area
                        toolbar_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'photo') or contains(@aria-label, 'Photo') or contains(@aria-label, 'media') or contains(@aria-label, 'Media')]")
                        for btn in toolbar_buttons:
                            if btn.is_displayed():
                                photo_button = btn
                                print(f"   ✅ Found photo button with aria-label")
                                break
                    except:
                        pass
                    
                    # Strategy 2: Look for the image icon button (it has an image/picture icon)
                    if not photo_button:
                        try:
                            # The photo button is usually the second icon in the toolbar
                            icon_buttons = self.driver.find_elements(By.XPATH, "//div[@role='textbox']/..//button[contains(@type, 'button')]")
                            if len(icon_buttons) >= 2:
                                photo_button = icon_buttons[1]  # Usually second button is photo
                                print(f"   ✅ Found photo button (second toolbar button)")
                        except:
                            pass
                    
                    # Strategy 3: JavaScript - look for any button with svg/image icon
                    if not photo_button:
                        try:
                            photo_buttons = self.driver.find_elements(By.XPATH, "//button[.//svg]")
                            for btn in photo_buttons:
                                # Check if button is in the composer area and visible
                                if btn.is_displayed() and "rewrite" not in btn.get_attribute("aria-label").lower():
                                    # Skip the "Rewrite with AI" button, get the media buttons
                                    parent = btn.find_element(By.XPATH, "..")
                                    if "Rewrite" not in btn.text:
                                        photo_button = btn
                                        print(f"   ✅ Found photo button via SVG icon")
                                        break
                        except:
                            pass
                    
                    if photo_button:
                        # Click the photo button
                        try:
                            photo_button.click()
                        except:
                            # Use JavaScript click if regular click fails
                            self.driver.execute_script("arguments[0].click();", photo_button)
                        
                        print("   ✅ Clicked photo button")
                        time.sleep(1)
                        
                        # Find the file input element
                        print("   Looking for file input...")
                        file_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                        )
                        
                        # Send the file path
                        abs_path = os.path.abspath(image_path)
                        file_input.send_keys(abs_path)
                        print(f"   ✅ Sent file path: {abs_path}")
                        
                        # Wait a moment for the file to be processed
                        time.sleep(1)
                        
                        # Close the Windows file picker dialog using pyautogui
                        print("   🔒 Closing Windows file picker dialog...")
                        try:
                            # Press ESC at the OS level to close the file picker
                            pyautogui.press('esc')
                            time.sleep(0.5)
                            print("   ✅ Pressed ESC to close dialog")
                        except Exception as e:
                            print(f"   ⚠️ Could not close dialog: {e}")
                        
                        # Wait for image to upload and editor to appear
                        print("   ⏳ Waiting for image editor to load...")
                        time.sleep(3)
                        
                        # Click "Next" button in the image editor
                        print("   🔍 Looking for 'Next' button...")
                        try:
                            next_button = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
                            )
                            next_button.click()
                            print("   ✅ Clicked 'Next' button")
                            time.sleep(2)
                        except Exception as e:
                            print(f"   ⚠️ Could not find 'Next' button, might not be needed: {e}")
                        
                        print("✅ Image upload complete!")
                        
                    else:
                        print("⚠️ Could not find photo upload button")
                        print("   Taking screenshot for debugging...")
                        self.driver.save_screenshot("debug_no_photo_button.png")
                        
                except Exception as e:
                    print(f"⚠️ Error uploading image: {e}")
                    print("   Taking screenshot...")
                    self.driver.save_screenshot("debug_image_upload_error.png")
                    print("   Continuing without image...")
            
            if full_auto:
                # FULL AUTO: Click the Post button
                print("🚀 Looking for Post button...")
                post_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Post']]"))
                )
                post_button.click()
                time.sleep(2)
                
                print("🎉 Post published automatically!")
                return True
            else:
                # SEMI-AUTO: Leave browser open for user to review and click Post
                print("✅ Post prepared! Review and click 'Post' button when ready.")
                print("   Browser will close after you click Post or press Enter here...")
                input("   Press Enter after posting...")
                return True
                
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            print("   Taking screenshot for debugging...")
            try:
                self.driver.save_screenshot("linkedin_error.png")
                print("   Screenshot saved to: linkedin_error.png")
            except:
                pass
            print("   Browser will stay open for debugging...")
            input("   Press Enter to close browser...")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

# Example usage functions
def post_victory_full_auto(post_text, screenshot_path, email=None, password=None):
    """Full automation - posts without user interaction"""
    poster = LinkedInPoster(headless=False)
    
    if poster.login(email, password):
        success = poster.post_to_linkedin(post_text, screenshot_path, full_auto=True)
        time.sleep(3)
        poster.close()
        return success
    else:
        poster.close()
        return False

def post_victory_semi_auto(post_text, screenshot_path, email=None, password=None):
    """Semi-auto - fills everything but user clicks Post"""
    poster = LinkedInPoster(headless=False)
    
    if poster.login(email, password):
        success = poster.post_to_linkedin(post_text, screenshot_path, full_auto=False)
        poster.close()
        return success
    else:
        poster.close()
        return False

def test_linkedin_connection():
    """Test if we can connect to LinkedIn and open post composer"""
    print("🧪 Testing LinkedIn Post Composer\n")
    poster = LinkedInPoster(headless=False)
    
    if poster.login():
        print("✅ LinkedIn connection successful!")
        print("\n📝 Now testing post composer with image...")
        
        # Test opening the post composer with dummy content
        test_post = "This is a test post from the Victory Royale Auto-Poster! 🎮\n\nTesting 1, 2, 3..."
        
        # Look for a victory screenshot to test with
        test_image = None
        if os.path.exists("victory_screenshots"):
            screenshots = [f for f in os.listdir("victory_screenshots") if f.endswith('.png')]
            if screenshots:
                test_image = os.path.join("victory_screenshots", screenshots[0])
                print(f"   Using test image: {test_image}")
        
        try:
            success = poster.post_to_linkedin(test_post, image_path=test_image, full_auto=False)
            if success:
                print("\n✅ Test successful! The composer opened, filled with text and image.")
            else:
                print("\n❌ Test failed.")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
    
    poster.close()

if __name__ == "__main__":
    # Quick test
    test_linkedin_connection()