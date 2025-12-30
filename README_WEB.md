# 🤖 RPA Bot - Web Interface

A powerful and intuitive web interface for the RPA (Robotic Process Automation) Bot with AI-powered task automation, web scraping, and desktop control.

## ✨ Features

- 🌐 **Modern Web Interface** - Beautiful, responsive UI that works in any browser
- 🤖 **AI-Powered** - Uses local LLM (via Ollama) to understand natural language tasks
- 🎬 **Web Automation** - YouTube searches, Google searches, and more via Selenium
- 🖥️ **Desktop Control** - Open applications, type text, take screenshots, and more
- 📊 **Real-time Logs** - Watch your automation execute with live feedback
- 🎤 **Voice Input** - Speak your commands (optional)
- 📝 **Example Tasks** - Quick-start with pre-built examples

## 🎯 What Can It Do?

### Web Automation
- ✅ Search and play YouTube videos
- ✅ Google searches
- ✅ Navigate websites
- ✅ Fill forms automatically

### Desktop Automation
- ✅ Open applications (Calculator, Notepad, etc.)
- ✅ Type text automatically
- ✅ Take screenshots
- ✅ Control keyboard and mouse
- ✅ Clipboard operations

### Example Commands
- *"Play song Despacito on YouTube"*
- *"Search for Python tutorial on YouTube"*
- *"Open calculator"*
- *"Take a screenshot"*
- *"Search for weather on Google"*
- *"Open notepad and type hello world"*

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running (for AI features)
3. **Chrome Browser** (for web automation)

### Installation

1. **Clone or download this project**

2. **Install Python dependencies:**
```bash
pip install -r requirements_web.txt
```

3. **Install and start Ollama:**

Download from: https://ollama.ai/

Then pull the model:
```bash
ollama pull llama2
```

Start Ollama server:
```bash
ollama serve
```

### Running the Web Interface

1. **Start the Flask server:**
```bash
python app.py
```

2. **Open your browser:**
```
http://localhost:5000
```

3. **Start automating!** 🎉

## 📖 How to Use

### Step 1: Enter Your Task
Type what you want to automate in natural language:
- Type in the text box, OR
- Click on an example task, OR
- Use voice input (if available)

### Step 2: Review Instructions
The AI will generate step-by-step instructions. Review them to make sure they're correct.

### Step 3: Execute
Click "Execute Task" and watch the automation run in real-time!

### Step 4: Monitor Progress
See live logs as each step executes. The browser will stay open for web tasks.

## 🏗️ Project Structure

```
OpenAI 2/
├── app.py                      # Flask web server
├── main_enhanced.py            # Core RPA logic
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── main.js            # Frontend logic
├── requirements_web.txt        # Python dependencies
└── README_WEB.md              # This file
```

## 🔧 Configuration

### Change LLM Model
Edit `app.py` or `main_enhanced.py`:
```python
self.model_name = "llama2"  # Change to your preferred model
```

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port
```

## 🐛 Troubleshooting

### "Ollama not running"
**Solution:** Start Ollama service
```bash
ollama serve
```

### "Selenium not available"
**Solution:** Install Chrome and dependencies
```bash
pip install selenium webdriver-manager
```

### "Speech recognition not available"
**Solution:** This is optional. To enable:
```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

### Web automation not working
**Solution:** Make sure Chrome browser is installed and updated

### Port 5000 already in use
**Solution:** Change the port in `app.py` or stop other services using port 5000
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

## 🎨 Features Breakdown

### Backend (Flask API)
- `/api/status` - Check system availability
- `/api/examples` - Get example tasks
- `/api/generate` - Generate instructions from natural language
- `/api/execute` - Execute RPA instructions
- `/api/logs/<session_id>` - Get execution logs
- `/api/speech` - Voice input (optional)

### Frontend Features
- ✨ Modern dark theme UI
- 📱 Fully responsive design
- 🔄 Real-time log updates
- 🎯 Step-by-step instruction display
- 🔔 Toast notifications
- ⚡ Fast and intuitive

## 🔒 Security Notes

- The server runs on `localhost` by default (safe for local use)
- Desktop automation has full system access (be careful with commands)
- For production use, add authentication and restrict capabilities

## 🚦 System Requirements

- **OS:** Windows 10/11, Linux, or macOS
- **RAM:** 4GB minimum (8GB recommended for LLM)
- **Python:** 3.8 or higher
- **Browser:** Chrome (latest version)
- **Ollama:** For AI features

## 💡 Tips & Best Practices

1. **Start Simple:** Try example tasks first
2. **Be Specific:** The more detailed your request, the better
3. **Review First:** Always review instructions before executing
4. **Watch Logs:** Monitor execution to catch any issues
5. **Close Browser:** Manually close browser windows when done with web tasks

## 🎯 Advanced Usage

### Custom Actions
Add new actions by extending the `RPAExecutor` class in `main_enhanced.py`

### Web Automation
Modify `WebAutomator` class for custom web automation tasks

### Styling
Customize colors and theme in `static/css/style.css`

## 📝 API Examples

### Generate Instructions
```javascript
fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task: 'Open calculator' })
})
```

### Execute Task
```javascript
fetch('/api/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        instructions: [...],
        session_id: 'unique-id'
    })
})
```

## 🤝 Contributing

Feel free to extend and customize this project for your needs!

## 📄 License

This project is for educational and personal use.

## 🙏 Acknowledgments

- Ollama for local LLM support
- Selenium for web automation
- PyAutoGUI for desktop automation
- Flask for the web framework

---

## 🎉 Enjoy Automating!

Have questions or issues? Check the troubleshooting section above.

**Happy Automating! 🤖✨**


