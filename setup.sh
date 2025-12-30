#!/bin/bash
# setup.sh

echo "Setting up RPA Bot with Local LLM..."

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (Linux/Mac)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull LLM model
ollama pull llama2

# For Windows users, download Ollama from https://ollama.ai

echo "Setup complete!"
echo "Run: python main.py"
