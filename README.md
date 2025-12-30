# RPA Bot - Intelligent Robotic Process Automation

An intelligent RPA (Robotic Process Automation) bot that converts natural language instructions into automated tasks. The bot supports desktop automation, web automation (YouTube, Google), and can be controlled via both command-line interface and web interface.

## 🚀 Features

### Core Capabilities
- **Natural Language Processing**: Converts plain English instructions into executable RPA tasks
- **Web Automation**: Automates YouTube searches, Google searches, and web interactions using Selenium
- **Desktop Automation**: Controls desktop applications, mouse, keyboard, and screen interactions
- **Multiple Input Methods**: 
  - Text input
  - Voice input (speech recognition)
  - Voice output (text-to-speech)
- **Web Interface**: Modern web-based UI for easy task management
- **LLM Integration**: Uses Ollama (local LLM) for intelligent task interpretation
- **Multiple Task Support**: Handles multiple instructions in a single command (e.g., "play song X and play song Y")

### Supported Actions
- `WEB_SEARCH`: Search on YouTube or Google
- `OPEN_APP`: Launch desktop applications (Calculator, Notepad, etc.)
- `OPEN_URL`: Open websites
- `CLICK`: Click at specific coordinates
- `TYPE`: Type text
- `SCREENSHOT`: Capture screenshots
- `WAIT`: Wait for specified duration
- `PRESS_KEY`: Press keyboard keys
- `HOTKEY`: Execute key combinations
- `SCROLL`: Scroll pages
- `COPY`/`PASTE`: Clipboard operations

## 📋 Prerequisites

- **Python 3.8+**
- **Google Chrome** (for web automation)
- **Ollama** (for LLM functionality)
  - Download from: https://ollama.ai
  - Install and run: `ollama serve`
  - Pull a model: `ollama pull llama2` (or your preferred model)

### Optional (for voice features)
- **Microphone** (for speech recognition)
- **Audio output** (for text-to-speech)

## 🛠️ Installation

### 1. Clone or Download the Project
```bash
cd "OpenAI 2"
```

### 2. Install Dependencies

#### Option A: Using requirements_web.txt (Recommended)
```bash
pip install -r requirements_web.txt
```

#### Option B: Manual Installation
```bash
pip install Flask Flask-CORS requests pyautogui pyperclip opencv-python Pillow numpy psutil selenium webdriver-manager SpeechRecognition pyttsx3 pyaudio
```

### 3. Setup Ollama
1. Install Ollama from https://ollama.ai
2. Start Ollama service:
   ```bash
   ollama serve
   ```
3. Pull a model (in a new terminal):
   ```bash
   ollama pull llama2
   ```

### 4. Verify Installation
```bash
python main.py
```

## 🎯 Usage

### Command-Line Interface

Run the main script:
```bash
python main.py
```

You'll see a menu with options:
1. **Type your task**: Enter natural language instructions
2. **Speak your task**: Use voice input (if microphone available)
3. **Example tasks**: Choose from predefined examples
4. **Exit**: Quit the application

#### Example Commands:
```
Play song Despacito on YouTube
Search for Python tutorial on YouTube
Open calculator and play music
Play song Shape of You and play song Despacito on YouTube
Take a screenshot
```

### Web Interface

#### Quick Start (Windows)
Double-click `start_web.bat` or run:
```bash
start_web.bat
```

#### Manual Start
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

#### Web Interface Features:
- **Task Input**: Enter natural language tasks
- **Instruction Preview**: See generated RPA instructions before execution
- **Real-time Logs**: Monitor execution progress
- **Example Tasks**: Quick access to common tasks
- **Status Monitoring**: Check system status (Ollama, Selenium, etc.)

## 📁 Project Structure

```
OpenAI 2/
├── main.py                 # Core RPA bot logic (CLI interface)
├── app.py                  # Flask web application
├── web_automation.py       # Web automation utilities
├── config.py              # Configuration management
├── requirements_web.txt   # Python dependencies
├── start_web.bat          # Windows launcher script
├── start_web.sh           # Linux/Mac launcher script
├── templates/
│   └── index.html         # Web interface HTML
├── static/
│   ├── css/
│   │   └── style.css      # Web interface styles
│   └── js/
│       └── main.js        # Web interface JavaScript
└── README.md              # This file
```

## ⚙️ Configuration

Configuration is managed through `config.py`. Default settings:

```python
{
    "llm_model": "codellama",           # Ollama model name
    "ollama_url": "http://127.0.0.1:11434/",
    "speech_enabled": True,
    "auto_execute": False,
    "screenshot_path": "./screenshots/",
    "log_level": "INFO"
}
```

To modify settings, edit `config.py` or create `rpa_config.json` in the project root.

## 🔧 How It Works

### Task Processing Flow

1. **User Input**: User provides natural language task
2. **LLM Processing**: Ollama LLM converts task to JSON instructions
3. **Fallback Logic**: If LLM fails, fallback parser extracts keywords
4. **Instruction Generation**: Creates structured RPA instructions
5. **Execution**: RPA executor performs the actions
6. **Logging**: All actions are logged for monitoring

### Multiple Instructions Support

The bot can handle multiple instructions in a single command:
- **Separators**: "and", "then", ",", "&"
- **Example**: "play song despacito and play song shape of you"
- **Result**: Generates 2 separate WEB_SEARCH instructions

## 📝 Example Tasks

### YouTube Tasks
```
Play song Despacito on YouTube
Search for Python tutorial on YouTube
Play music Shape of You on YouTube
Watch video Gangnam Style
```

### Google Tasks
```
Search for weather on Google
Search for news on Google
```

### Desktop Tasks
```
Open calculator
Open notepad
Take a screenshot
```

### Combined Tasks
```
Open calculator and play music
Play song Despacito and play song Shape of You on YouTube
Search for Python tutorial and search for JavaScript tutorial on YouTube
```

## 🔒 Security Notes

- The bot has access to your desktop and can perform actions automatically
- Use with caution in production environments
- Review generated instructions before execution
- The web interface runs on `0.0.0.0` by default (accessible from network)

## 🚧 Limitations

- Requires Ollama to be running for LLM features
- Web automation requires Chrome browser
- Speech recognition quality depends on microphone and environment
- Some actions may require manual intervention
- Windows-focused (some features may not work on Linux/Mac)

## 📚 Dependencies

### Core Dependencies
- `Flask` - Web framework
- `selenium` - Web automation
- `pyautogui` - Desktop automation
- `requests` - HTTP requests
- `Pillow` - Image processing
- `opencv-python` - Computer vision

### Optional Dependencies
- `SpeechRecognition` - Voice input
- `pyttsx3` - Text-to-speech
- `pyaudio` - Audio I/O

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for more web platforms
- Additional desktop applications
- Better error handling
- Cross-platform compatibility
- More LLM models support

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **Selenium** - Web automation framework
- **Flask** - Web framework
- **PyAutoGUI** - Desktop automation

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check Ollama and Selenium documentation

---

**Made with ❤️ for automation enthusiasts**

