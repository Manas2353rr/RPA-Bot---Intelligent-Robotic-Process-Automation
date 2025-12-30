# config.py
import json

class Config:
    def __init__(self):
        self.config_file = "rpa_config.json"
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.default_config()
            self.save_config()
    
    def default_config(self):
        return {
            "llm_model": "codellama",
            "ollama_url": "http://127.0.0.1:11434/",
            "speech_enabled": True,
            "auto_execute": False,
            "screenshot_path": "./screenshots/",
            "log_level": "INFO"
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key):
        return self.config.get(key)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
