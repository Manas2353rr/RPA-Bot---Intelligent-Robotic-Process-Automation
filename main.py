# main.py - Flask Web Application for RPA Bot

import json
import time
import subprocess
import webbrowser
import pyautogui
import pyperclip
import requests
import config
import os
from web_automation import WebAutomation


import logging
import threading
from PIL import Image
import psutil

# Web automation imports
''' from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    optional: options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service, options=options) '''

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    print("✅ Web automation available")
except ImportError as e:
    print(f"⚠️  Web automation not available: {e}")
    print("💡 Install with: pip install selenium webdriver-manager")
    SELENIUM_AVAILABLE = False

# Optional imports with graceful fallbacks
SPEECH_AVAILABLE = False
TTS_AVAILABLE = False

try:
    import speech_recognition as sr

    try:
        r = sr.Recognizer()

        mic = sr.Microphone()
       # r = sr.Recognizer()
      #  mic = sr.Microphone()

        SPEECH_AVAILABLE = True
        print("✅ Speech recognition available")
    except Exception as e:
        print(f"⚠️  Speech recognition hardware issue: {e}")
        SPEECH_AVAILABLE = False
except ImportError as e:
    print(f"⚠️  Speech recognition not available: {e}")

try:
    import pyttsx3
    try:
        engine = pyttsx3.init()
        TTS_AVAILABLE = True
        print("✅ Text-to-speech available")
    except Exception as e:
        print(f"⚠️  TTS engine issue: {e}")
        TTS_AVAILABLE = False
except ImportError as e:
    print(f"⚠️  Text-to-speech not available: {e}")

class RPABot:
    def __init__(self):
        self.setup_logging()
        self.setup_speech()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama2"
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_speech(self):
        """Setup speech recognition and TTS if available"""
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        if SPEECH_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Microphone access confirmed")
            except Exception as e:
                print(f"⚠️  Microphone setup failed: {e}")
                self.recognizer = None
                self.microphone = None
                
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    print("✅ TTS engine ready")
            except Exception as e:
                print(f"⚠️  TTS setup failed: {e}")
                self.tts_engine = None
        
    def listen_to_speech(self):
        """Convert speech to text"""
        if not self.recognizer or not self.microphone:
            print("❌ Speech recognition not available")
            return None
            
        try:
            print("🎤 Listening... (Speak clearly)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🔴 Recording... Speak now!")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"🗣️  You said: '{text}'")
            return text
            
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech or print"""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"⚠️  TTS error: {e}")
                print(f"🔊 Bot: {text}")
        else:
            print(f"🔊 Bot: {text}")
    
    def check_ollama_connection(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print(f"✅ Ollama connected. Available models: {[m['name'] for m in models]}")
                    return True
                else:
                    print("⚠️  Ollama connected but no models found. Run: ollama pull llama2")
                    return False
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Ollama not running. Start with: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
            return False
    
    def query_llm(self, prompt):
        """Query the local LLM via Ollama"""
        if not self.check_ollama_connection():
            return None
            
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            }
            
            print("🤖 Querying local LLM...")
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()["response"]
                print("✅ LLM response received")
                return result
            else:
                self.logger.error(f"LLM request failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error querying LLM: {e}")
            return None
    
    def extract_search_terms(self, user_task):
        """Extract search terms from user task - handles multiple instructions"""
        task_lower = user_task.lower()
        
        # Common patterns for YouTube searches
        patterns = [
            "play song",
            "play music",
            "search for",
            "find song",
            "listen to",
            "watch video",
            "play video"
        ]
        
        # Split by common separators to handle multiple instructions
        separators = [" and ", " then ", " , ", " & "]
        tasks = [user_task]
        
        for sep in separators:
            new_tasks = []
            for task in tasks:
                if sep in task.lower():
                    new_tasks.extend([t.strip() for t in task.split(sep)])
                else:
                    new_tasks.append(task.strip())
            tasks = new_tasks
        
        search_terms = []
        
        for task in tasks:
            task_lower = task.lower()
            search_term = task
            
            for pattern in patterns:
                if pattern in task_lower:
                    # Remove the pattern and get the actual search term
                    search_term = task_lower.replace(pattern, "").strip()
                    # Remove common words
                    search_term = search_term.replace("on youtube", "").strip()
                    search_term = search_term.replace("youtube", "").strip()
                    break
            
            # Clean up the search term
            search_term = search_term.strip()
            if search_term and search_term not in search_terms:
                search_terms.append(search_term)
        
        return search_terms if search_terms else ["music"]
    
    def generate_rpa_instructions(self, user_task):
        """Generate RPA instructions from natural language task"""
        
        system_prompt = f"""You are an RPA expert. Convert this task to JSON instructions.

Available actions:
- OPEN_APP: Open application
- OPEN_URL: Open website
- WEB_SEARCH: Search on a website (YouTube, Google, etc.)
- WEB_CLICK: Click web element by text, ID, or CSS selector
- WEB_TYPE: Type in web input field
- WEB_WAIT: Wait for web element to load
- CLICK: Click coordinates
- TYPE: Type text
- SCREENSHOT: Take screenshot
- WAIT: Wait specified seconds
- PRESS_KEY: Press keyboard key
- HOTKEY: Key combinations

IMPORTANT: For YouTube tasks, use WEB_SEARCH action!

Examples:

Task: "play song despacito on youtube"
Output: [
  {{"action": "WEB_SEARCH", "params": {{"site": "youtube", "query": "despacito", "auto_play": true}}}}
]

Task: "search for python tutorial on youtube"
Output: [
  {{"action": "WEB_SEARCH", "params": {{"site": "youtube", "query": "python tutorial", "auto_play": false}}}}
]

Task: "open google and search for weather"
Output: [
  {{"action": "WEB_SEARCH", "params": {{"site": "google", "query": "weather", "auto_play": false}}}}
]

Task: "open calculator and chrome"
Output: [
  {{"action": "OPEN_APP", "params": {{"app": "calc", "wait_time": 3}}}},
  {{"action": "WAIT", "params": {{"seconds": 2}}}},
  {{"action": "OPEN_URL", "params": {{"url": "https://google.com", "wait_time": 4}}}}
]

Now convert this task: "{user_task}"
Output:"""

        response = self.query_llm(system_prompt)
        
        if response:
            try:
                response = response.strip()
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    instructions = json.loads(json_str)
                    return instructions
                else:
                    print("❌ No valid JSON found in LLM response")
                    return self.create_fallback_instructions(user_task)
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                return self.create_fallback_instructions(user_task)
        
        return self.create_fallback_instructions(user_task)
    
    def create_fallback_instructions(self, user_task):
        """Create fallback instructions when LLM fails"""
        task_lower = user_task.lower()
        instructions = []
        
        # YouTube-related tasks
        if any(word in task_lower for word in ["play", "song", "music", "youtube", "video"]):
            search_terms = self.extract_search_terms(user_task)
            auto_play = "play" in task_lower
            
            # Create an instruction for each search term
            for search_term in search_terms:
                instructions.append({
                    "action": "WEB_SEARCH", 
                    "params": {
                        "site": "youtube", 
                        "query": search_term, 
                        "auto_play": auto_play
                    }
                })
        
        # Google search
        elif "google" in task_lower and "search" in task_lower:
            search_term = task_lower.replace("google", "").replace("search", "").replace("for", "").strip()
            instructions.append({
                "action": "WEB_SEARCH",
                "params": {
                    "site": "google",
                    "query": search_term,
                    "auto_play": False
                }
            })
        
        # App opening
        elif "calculator" in task_lower or "calc" in task_lower:
            instructions.append({"action": "OPEN_APP", "params": {"app": "calc", "wait_time": 3}})
            
        elif "notepad" in task_lower:
            instructions.append({"action": "OPEN_APP", "params": {"app": "notepad", "wait_time": 3}})
            
        elif "screenshot" in task_lower:
            instructions.append({"action": "SCREENSHOT", "params": {"filename": "screenshot.png"}})
        
        return instructions if instructions else None

class WebAutomator:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available for web automation")
            return False
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome driver initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def search_youtube(self, query, auto_play=True):
        """Search and optionally play video on YouTube"""
        try:
            print(f"🎵 Searching YouTube for: '{query}'")
            
            # Go to YouTube
            self.driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # Find and click search box
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            print("🔍 Search submitted, waiting for results...")
            time.sleep(3)
            
            if auto_play:
                # Click on the first video
                try:
                    # Wait for video thumbnails to load
                    first_video = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
                    )
                    
                    video_title = first_video.get_attribute("title")
                    print(f"🎬 Playing: {video_title}")
                    
                    first_video.click()
                    time.sleep(5)  # Wait for video to load
                    
                    print("✅ Video should now be playing!")
                    return True
                    
                except Exception as e:
                    print(f"⚠️  Could not auto-play video: {e}")
                    print("📺 Search results are displayed")
                    return True
            else:
                print("📺 Search results displayed")
                return True
                
        except Exception as e:
            print(f"❌ YouTube search failed: {e}")
            return False
    
    def search_google(self, query):
        """Search on Google"""
        try:
            print(f"🔍 Searching Google for: '{query}'")
            
            self.driver.get("https://www.google.com")
            time.sleep(2)
            
            # Find search box (Google has different possible names)
            search_selectors = ["q", "search"]
            search_box = None
            
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.NAME, selector)
                    break
                except:
                    continue
            
            if not search_box:
                # Try by CSS selector
                search_box = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(3)
            print("✅ Google search completed")
            return True
            
        except Exception as e:
            print(f"❌ Google search failed: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser closed")
            except:
                pass

class RPAExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        self.opened_processes = []
        self.web_automator = WebAutomator()
        
    def is_process_running(self, process_name):
        """Check if a process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
        except:
            pass
        return False
    
    def execute_instructions(self, instructions):
        """Execute the RPA instructions"""
        print(f"🚀 Executing {len(instructions)} instructions...")
        
        web_actions_present = any(
            inst.get("action", "").startswith("WEB_") 
            for inst in instructions
        )
        
        if web_actions_present:
            if not self.web_automator.setup_driver():
                print("❌ Cannot perform web actions without browser automation")
                return
        
        for i, instruction in enumerate(instructions):
            try:
                print(f"\n🔄 Step {i+1}/{len(instructions)}: {instruction}")
                action = instruction.get("action")
                params = instruction.get("params", {})
                
                if action == "WEB_SEARCH":
                    self.web_search_action(params)
                elif action == "OPEN_APP":
                    self.open_app_action(params)
                elif action == "OPEN_URL":
                    self.open_url_action(params)
                elif action == "CLICK":
                    self.click_action(params)
                elif action == "TYPE":
                    self.type_action(params)
                elif action == "SCREENSHOT":
                    self.screenshot_action(params)
                elif action == "WAIT":
                    self.wait_action(params)
                elif action == "COPY":
                    self.copy_action()
                elif action == "PASTE":
                    self.paste_action()
                elif action == "SCROLL":
                    self.scroll_action(params)
                elif action == "PRESS_KEY":
                    self.press_key_action(params)
                elif action == "HOTKEY":
                    self.hotkey_action(params)
                else:
                    print(f"❌ Unknown action: {action}")
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error in step {i+1}: {e}")
                continue
                
        print("\n✅ All instructions completed!")
        
        # Keep browser open for web actions
        if web_actions_present:
            input("\n🌐 Browser is open. Press Enter to close it...")
            self.web_automator.close()
    
    def web_search_action(self, params):
        """Perform web search"""
        site = params.get("site", "google").lower()
        query = params.get("query", "")
        auto_play = params.get("auto_play", False)
        
        if not query:
            print("❌ No search query provided")
            return
            
        if site == "youtube":
            self.web_automator.search_youtube(query, auto_play)
        elif site == "google":
            self.web_automator.search_google(query)
        else:
            print(f"❌ Unsupported search site: {site}")
    
    def open_app_action(self, params):
        """Open application"""
        app_name = params.get("app", "")
        wait_time = params.get("wait_time", 3)
        
        try:
            app_map = {
                "calc": {"exe": "calc.exe", "process": "Calculator"},
                "calculator": {"exe": "calc.exe", "process": "Calculator"}, 
                "notepad": {"exe": "notepad.exe", "process": "notepad"},
                "paint": {"exe": "mspaint.exe", "process": "mspaint"},
            }
            
            app_info = app_map.get(app_name.lower())
            if app_info:
                exe_name = app_info["exe"]
                process_name = app_info["process"]
                
                if self.is_process_running(process_name):
                    print(f"⚠️  {app_name} is already running")
                    return
                
                print(f"🚀 Starting {app_name}...")
                process = subprocess.Popen(exe_name, shell=True)
                self.opened_processes.append(process)
                time.sleep(wait_time)
                print(f"✅ {app_name} opened")
                
        except Exception as e:
            print(f"❌ Failed to open {app_name}: {e}")
    
    def open_url_action(self, params):
        """Open URL"""
        url = params.get("url", "")
        wait_time = params.get("wait_time", 4)
        
        if url:
            print(f"🌐 Opening URL: {url}")
            webbrowser.open(url)
            time.sleep(wait_time)
    
    def click_action(self, params):
        if "x" in params and "y" in params:
            pyautogui.click(params["x"], params["y"])
            print(f"✅ Clicked at ({params['x']}, {params['y']})")
        else:
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2)
            print("✅ Clicked center of screen")
    
    def type_action(self, params):
        text = params.get("text", "")
        interval = params.get("interval", 0.05)
        time.sleep(0.5)
        pyautogui.typewrite(text, interval=interval)
        print(f"✅ Typed: '{text}'")
    
    def screenshot_action(self, params):
        filename = params.get("filename", f"screenshot_{int(time.time())}.png")
        try:
            time.sleep(1)
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            print(f"✅ Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
    
    def wait_action(self, params):
        seconds = params.get("seconds", 1)
        print(f"⏳ Waiting {seconds} seconds...")
        time.sleep(seconds)
    
    def copy_action(self):
        pyautogui.hotkey('ctrl', 'c')
        print("✅ Copied to clipboard")
    
    def paste_action(self):
        pyautogui.hotkey('ctrl', 'v')
        print("✅ Pasted from clipboard")
    
    def scroll_action(self, params):
        direction = params.get("direction", "down")
        clicks = params.get("clicks", 3)
        
        if direction.lower() == "up":
            pyautogui.scroll(clicks)
        else:
            pyautogui.scroll(-clicks)
        print(f"✅ Scrolled {direction}")
    
    def press_key_action(self, params):
        key = params.get("key", "")
        if key:
            pyautogui.press(key.lower())
            print(f"✅ Pressed: {key}")
    
    def hotkey_action(self, params):
        keys = params.get("keys", [])
        if keys:
            pyautogui.hotkey(*keys)
            print(f"✅ Hotkey: {'+'.join(keys)}")
    
    def cleanup(self):
        """Clean up resources"""
        self.web_automator.close()
        for process in self.opened_processes:
            try:
                if process.poll() is None:
                    process.terminate()
            except:
                pass

def main():
    print("🤖 RPA Bot with Web Automation - YouTube & Google Search")
    print("=" * 65)
    
    bot = RPABot()
    executor = RPAExecutor()
    
    features = []
    if SPEECH_AVAILABLE and bot.recognizer:
        features.append("🎤 Speech input")
    if TTS_AVAILABLE and bot.tts_engine:
        features.append("🔊 Voice output")
    if SELENIUM_AVAILABLE:
        features.append("🌐 Web automation")
    features.extend(["⌨️  Text input", "🖱️  Desktop automation"])
    
    print("Available features:", " | ".join(features))
    
    try:
        while True:
            print("\n" + "="*65)
            print("📋 Choose input method:")
            print("1. Type your task")
            
            if SPEECH_AVAILABLE and bot.recognizer:
                print("2. Speak your task")
                print("3. Example tasks")
                print("4. Exit")
                max_choice = 4
            else:
                print("2. Example tasks") 
                print("3. Exit")
                max_choice = 3
            
            try:
                choice = input(f"\nEnter choice (1-{max_choice}): ").strip()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            
            user_task = None
            
            if choice == "1":
                user_task = input("\n💬 Enter your task: ").strip()
                
            elif choice == "2" and SPEECH_AVAILABLE and bot.recognizer:
                user_task = bot.listen_to_speech()
                
            elif (choice == "2" and not SPEECH_AVAILABLE) or (choice == "3" and SPEECH_AVAILABLE):
                print("\n💡 Example tasks:")
                examples = [
                    "Play song Despacito on YouTube",
                    "Play music Shape of You on YouTube", 
                    "Search for Python tutorial on YouTube",
                    "Search for weather on Google",
                    "Open calculator and play music",
                    "Take a screenshot",
                    "Play video Gangnam Style",
                    "Search for news on Google"
                ]
                
                for i, example in enumerate(examples, 1):
                    print(f"   {i}. {example}")
                
                try:
                    ex_choice = int(input(f"\nSelect example (1-{len(examples)}): ")) - 1
                    if 0 <= ex_choice < len(examples):
                        user_task = examples[ex_choice]
                    else:
                        print("❌ Invalid selection")
                        continue
                except ValueError:
                    print("❌ Please enter a number")
                    continue
                    
            elif choice == str(max_choice):
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice!")
                continue
            
            if user_task:
                print(f"\n🎯 Task: {user_task}")
                bot.speak("Processing your task")
                
                instructions = bot.generate_rpa_instructions(user_task)
                
                if instructions:
                    print(f"\n📋 Generated {len(instructions)} instructions:")
                    for i, inst in enumerate(instructions, 1):
                        action = inst.get('action', 'Unknown')
                        params = inst.get('params', {})
                        
                        if action == "WEB_SEARCH":
                            site = params.get('site', 'unknown')
                            query = params.get('query', 'unknown')
                            auto_play = params.get('auto_play', False)
                            play_text = " and play" if auto_play else ""
                            print(f"   {i}. Search {site} for '{query}'{play_text}")
                        elif action == "OPEN_APP":
                            app = params.get('app', 'Unknown')
                            print(f"   {i}. Open {app}")
                        else:
                            print(f"   {i}. {action}: {params}")
                    
                    print(f"\n🚀 Executing task...")
                    bot.speak("Executing your task now")
                    executor.execute_instructions(instructions)
                    bot.speak("Task completed successfully")
                else:
                    print("❌ Could not generate instructions")
                    bot.speak("Sorry, I couldn't process that task")
                    
    except KeyboardInterrupt:
        print("\n👋 Program interrupted. Goodbye!")
    finally:
        executor.cleanup()

if __name__ == "__main__":
    main()
