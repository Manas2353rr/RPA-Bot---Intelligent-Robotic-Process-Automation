# app.py - Flask Web Application for RPA Bot
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import time
import threading
import queue
import os
from datetime import datetime

# Import from main_enhanced
from main import RPABot, RPAExecutor, WebAutomator, SELENIUM_AVAILABLE, SPEECH_AVAILABLE, TTS_AVAILABLE

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Global variables for managing execution
execution_logs = {}
execution_status = {}
active_executors = {}  # Keep executors alive to prevent browser from closing

class LogCapture:
    """Capture logs from RPA execution"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.logs = []
        
    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "level": level
        }
        self.logs.append(log_entry)
        
        # Store in global dict
        if self.session_id not in execution_logs:
            execution_logs[self.session_id] = []
        execution_logs[self.session_id].append(log_entry)
        
    def get_logs(self):
        return self.logs

class WebRPAExecutor(RPAExecutor):
    """Extended RPA Executor with logging capability"""
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        
    def execute_instructions(self, instructions):
        """Execute instructions with logging"""
        self.logger.log(f"🚀 Starting execution of {len(instructions)} instructions", "info")
        
        web_actions_present = any(
            inst.get("action", "").startswith("WEB_") 
            for inst in instructions
        )
        
        if web_actions_present:
            if not self.web_automator.setup_driver():
                self.logger.log("❌ Cannot perform web actions without browser automation", "error")
                return False
        
        try:
            for i, instruction in enumerate(instructions):
                action = instruction.get("action")
                params = instruction.get("params", {})
                
                self.logger.log(f"🔄 Step {i+1}/{len(instructions)}: {action}", "info")
                
                try:
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
                        self.logger.log(f"❌ Unknown action: {action}", "error")
                        
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.log(f"❌ Error in step {i+1}: {str(e)}", "error")
                    continue
                    
            self.logger.log("✅ All instructions completed!", "success")
            
            # Keep browser open for web actions
            if web_actions_present:
                self.logger.log("🌐 Browser is open. You can close it manually when done.", "info")
                
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Execution failed: {str(e)}", "error")
            return False
    
    def web_search_action(self, params):
        super().web_search_action(params)
        site = params.get("site", "google")
        query = params.get("query", "")
        self.logger.log(f"🔍 Searching {site} for: '{query}'", "info")
    
    def open_app_action(self, params):
        super().open_app_action(params)
        app_name = params.get("app", "")
        self.logger.log(f"✅ Opened application: {app_name}", "success")
        
    def screenshot_action(self, params):
        super().screenshot_action(params)
        filename = params.get("filename", "screenshot.png")
        self.logger.log(f"📸 Screenshot saved: {filename}", "success")

# Initialize bot globally
rpa_bot = RPABot()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        "ollama_connected": rpa_bot.check_ollama_connection(),
        "selenium_available": SELENIUM_AVAILABLE,
        "speech_available": SPEECH_AVAILABLE,
        "tts_available": TTS_AVAILABLE
    })

@app.route('/api/examples')
def get_examples():
    """Get example tasks"""
    examples = [
        "Play song Despacito on YouTube",
        "Play music Shape of You on YouTube", 
        "Search for Python tutorial on YouTube",
        "Search for weather on Google",
        "Open calculator",
        "Take a screenshot",
        "Open notepad and type hello world",
        "Search for news on Google"
    ]
    return jsonify({"examples": examples})

@app.route('/api/generate', methods=['POST'])
def generate_instructions():
    """Generate RPA instructions from task"""
    data = request.json
    user_task = data.get('task', '')
    
    if not user_task:
        return jsonify({"error": "No task provided"}), 400
    
    try:
        instructions = rpa_bot.generate_rpa_instructions(user_task)
        
        if instructions:
            # Generate session ID
            session_id = str(int(time.time() * 1000))
            
            return jsonify({
                "success": True,
                "instructions": instructions,
                "session_id": session_id,
                "count": len(instructions)
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not generate instructions for this task"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/execute', methods=['POST'])
def execute_task():
    """Execute RPA instructions"""
    data = request.json
    instructions = data.get('instructions', [])
    session_id = data.get('session_id', str(int(time.time() * 1000)))
    
    if not instructions:
        return jsonify({"error": "No instructions provided"}), 400
    
    # Initialize logging for this session
    execution_logs[session_id] = []
    execution_status[session_id] = "running"
    
    def execute_in_background():
        logger = LogCapture(session_id)
        executor = WebRPAExecutor(logger)
        
        # Store executor globally to prevent garbage collection (keeps browser open)
        active_executors[session_id] = executor
        
        try:
            success = executor.execute_instructions(instructions)
            execution_status[session_id] = "completed" if success else "failed"
        except Exception as e:
            logger.log(f"Fatal error: {str(e)}", "error")
            execution_status[session_id] = "failed"
    
    # Start execution in background thread
    thread = threading.Thread(target=execute_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": "Execution started"
    })

@app.route('/api/logs/<session_id>')
def get_logs(session_id):
    """Get execution logs for a session"""
    logs = execution_logs.get(session_id, [])
    status = execution_status.get(session_id, "unknown")
    
    return jsonify({
        "logs": logs,
        "status": status
    })

@app.route('/api/close-browser/<session_id>', methods=['POST'])
def close_browser(session_id):
    """Close browser for a specific session"""
    try:
        if session_id in active_executors:
            executor = active_executors[session_id]
            executor.web_automator.close()
            del active_executors[session_id]
            return jsonify({
                "success": True,
                "message": "Browser closed"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No active session found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/speech', methods=['POST'])
def speech_to_text():
    """Convert speech to text"""
    if not SPEECH_AVAILABLE or not rpa_bot.recognizer:
        return jsonify({
            "success": False,
            "error": "Speech recognition not available"
        }), 400
    
    try:
        text = rpa_bot.listen_to_speech()
        if text:
            return jsonify({
                "success": True,
                "text": text
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not recognize speech"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting RPA Bot Web Interface...")
    print("📱 Open your browser to: http://localhost:5000")
    print("=" * 60)
    
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

