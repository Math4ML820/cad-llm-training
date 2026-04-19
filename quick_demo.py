#!/usr/bin/env python3
"""
Quick CAD Demo - Optimized for Limited Resources

Tests only the Gemma model with faster loading and better error handling.
"""

import requests
import time
import re

def test_cad_generation():
    """Simple CAD generation test"""
    ollama_url = "http://localhost:11434"
    model = "gemma3:1b"
    
    # Check connection
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not running. Start with: ollama serve")
            return
    except:
        print("❌ Cannot connect to Ollama. Start with: ollama serve")
        return
    
    print("✅ Ollama connected")
    
    # Test cases showing the problem we're solving
    test_cases = [
        "create a sphere radius 3",
        "make a cylinder radius 2 height 5", 
        "generate a cube 4 by 4 by 4"
    ]
    
    print(f"\n🎯 Testing {model} on CAD generation:")
    print("=" * 60)
    
    for i, instruction in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{instruction}'")
        
        # Simple prompt without complex system prompts
        prompt = f"Generate OpenSCAD code: {instruction}\nCode:"
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 50  # Limit output length
                    }
                },
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()["response"].strip()
                # Clean result
                result = re.sub(r'```[a-zA-Z]*\n?', '', result)
                result = re.sub(r'```', '', result)
                result = result.split('\n')[0].strip()  # First line only
                
                # Validate
                is_correct = validate_result(result, instruction)
                status = "✅ Correct" if is_correct else "❌ Wrong"
                
                print(f"   Output: {result}")
                print(f"   Status: {status} ({elapsed:.1f}s)")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ❌ Timeout (model still loading...)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("💡 Analysis:")
    print("- If you see cubes for sphere requests, the model needs training!")
    print("- This demonstrates why we need the fine-tuning pipeline.")
    print("- Run 'python3 demo.py' for the full interactive version.")

def validate_result(result, instruction):
    """Simple validation"""
    instruction_lower = instruction.lower()
    
    if 'sphere' in instruction_lower:
        return 'sphere(' in result
    elif 'cylinder' in instruction_lower:
        return 'cylinder(' in result
    elif 'cube' in instruction_lower or 'box' in instruction_lower:
        return 'cube(' in result
    
    return True  # Default to true for unknown shapes

if __name__ == "__main__":
    test_cad_generation()