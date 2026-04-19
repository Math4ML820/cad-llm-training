#!/usr/bin/env python3
"""
Quick Start Script for CAD LLM Pipeline

Automatically sets up and runs the demo system.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_ollama():
    """Check if Ollama is running and install if needed"""
    print("🔍 Checking Ollama installation...")
    
    try:
        # Check if ollama command exists
        result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Ollama not found")
            print("Installing Ollama...")
            subprocess.run(['brew', 'install', 'ollama'], check=True)
            print("✅ Ollama installed")
        else:
            print("✅ Ollama found")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Ollama via brew")
        print("Please install manually: https://ollama.ai/download")
        return False
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
    except:
        pass
    
    print("🚀 Starting Ollama service...")
    # Start Ollama in background
    subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for service to start
    for i in range(10):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                print("✅ Ollama service started")
                return True
        except:
            time.sleep(1)
    
    print("❌ Failed to start Ollama service")
    return False

def download_models():
    """Download required models"""
    print("📥 Checking and downloading models...")
    
    models = ['gemma3:1b', 'llama3', 'mistral']
    
    # Get current models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        current_models = []
        if response.status_code == 200:
            for model in response.json().get('models', []):
                current_models.append(model['name'])
        
        for model in models:
            model_exists = any(model in existing for existing in current_models)
            if not model_exists:
                print(f"📥 Downloading {model}...")
                result = subprocess.run(['ollama', 'pull', model], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {model} downloaded")
                else:
                    print(f"⚠️  Failed to download {model}, but continuing...")
            else:
                print(f"✅ {model} already available")
        
        return True
    except Exception as e:
        print(f"⚠️  Error checking models: {e}")
        return False

def generate_data():
    """Generate training data if needed"""
    data_file = Path("data/cad_training_data.json")
    
    if data_file.exists():
        print("✅ Training data already exists")
        return True
    
    print("🔧 Generating training data...")
    try:
        result = subprocess.run([sys.executable, 'generate_training_data.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Training data generated")
            return True
        else:
            print(f"❌ Failed to generate data: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        return False

def run_demo():
    """Run the interactive demo"""
    print("🎯 Starting CAD LLM Demo...")
    print("="*50)
    
    try:
        subprocess.run([sys.executable, 'demo.py'])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")

def main():
    """Main setup and launch sequence"""
    print("🚀 CAD LLM Pipeline - Quick Start")
    print("="*40)
    
    # Step 1: Setup Ollama
    if not check_ollama():
        print("❌ Setup failed. Please install Ollama manually.")
        return
    
    # Step 2: Download models
    if not download_models():
        print("⚠️  Some models may not be available, but continuing...")
    
    # Step 3: Generate data
    if not generate_data():
        print("❌ Failed to generate training data")
        return
    
    print("\n" + "="*50)
    print("✅ SETUP COMPLETE!")
    print("="*50)
    print("Your CAD LLM system is ready!")
    print("\nAvailable commands:")
    print("- python3 demo.py           # Interactive model comparison")
    print("- python3 compare_models.py # Full performance benchmark")
    print("- python3 train_models.py   # Train custom models")
    print("="*50)
    
    # Step 4: Launch demo
    try:
        choice = input("\nRun interactive demo now? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '']:
            run_demo()
        else:
            print("👍 Setup complete. Run 'python3 demo.py' when ready!")
    except KeyboardInterrupt:
        print("\n👋 Setup complete!")

if __name__ == "__main__":
    main()