#!/usr/bin/env python3
"""
CAD Generation Demo - Interactive Model Comparison

This script provides live comparison of different LLM models for CAD code generation,
showing the dramatic improvements from proper training data and model selection.
"""

import requests
import json
import time
import re
from typing import Dict, List, Tuple, Optional

class CADModelDemo:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.models = {
            "gemma": "gemma3:1b"
            # Temporarily disabled larger models due to memory constraints
            # "llama": "llama3",
            # "mistral": "mistral"
        }
        
        # Enhanced system prompt for CAD generation
        self.system_prompt = """You are an expert OpenSCAD code generator. Generate ONLY valid OpenSCAD code without explanations.

Rules:
1. Output only the code, no markdown or explanations
2. End statements with semicolons
3. Use exact syntax:
   - Cubes: cube([x, y, z]);
   - Spheres: sphere(r=radius);
   - Cylinders: cylinder(r=radius, h=height);
   - Cones: cylinder(r1=r1, r2=r2, h=height);
   - Torus: rotate_extrude() translate([R,0,0]) circle(r=r);
4. No comments, no explanatory text, no markdown code blocks

Examples:
Input: Create a box 2 by 3 by 4
Output: cube([2, 3, 4]);

Input: Generate a sphere radius 1.5
Output: sphere(r=1.5);

Input: Make a cylinder radius 2 height 8
Output: cylinder(r=2, h=8);"""
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available = []
                for model in models_data.get('models', []):
                    model_name = model['name']
                    # Map back to our short names
                    for short_name, full_name in self.models.items():
                        if full_name in model_name:
                            available.append(short_name)
                            break
                return available
            return []
        except:
            return []
    
    def query_model(self, model: str, instruction: str) -> Dict:
        """Query a model and return results with timing and validation"""
        if model not in self.models:
            return {"error": f"Unknown model: {model}"}
        
        model_name = self.models[model]
        full_prompt = f"{self.system_prompt}\n\nInput: {instruction}\nOutput:"
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                },
                timeout=120  # Increased timeout for model loading
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                raw_response = response.json()["response"]
                cleaned_response = self.clean_response(raw_response)
                is_valid = self.validate_response(cleaned_response, instruction)
                
                return {
                    "model": model,
                    "instruction": instruction,
                    "raw_response": raw_response,
                    "cleaned_response": cleaned_response,
                    "is_valid": is_valid,
                    "response_time": elapsed_time,
                    "success": True
                }
            else:
                return {
                    "model": model,
                    "error": f"HTTP {response.status_code}",
                    "response_time": elapsed_time,
                    "success": False
                }
                
        except requests.exceptions.Timeout:
            return {
                "model": model,
                "error": "Request timed out (model may be loading)",
                "response_time": 120.0,
                "success": False
            }
        except Exception as e:
            return {
                "model": model,
                "error": str(e),
                "response_time": time.time() - start_time,
                "success": False
            }
    
    def clean_response(self, response: str) -> str:
        """Clean the response to extract only OpenSCAD code"""
        # Remove markdown
        response = re.sub(r'```[a-zA-Z]*\n', '', response)
        response = re.sub(r'```', '', response)
        
        # Extract lines that look like OpenSCAD code
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if any(func in line for func in ['cube(', 'cylinder(', 'sphere(', 'rotate_extrude()']):
                if not line.endswith(';'):
                    line += ';'
                return line
        
        # If no obvious code found, return cleaned result
        return response.strip()
    
    def validate_response(self, response: str, instruction: str) -> Dict:
        """Validate response and return detailed scoring"""
        score = 0.0
        details = []
        
        # Check if response contains valid OpenSCAD functions
        valid_functions = ['cube(', 'cylinder(', 'sphere(', 'rotate_extrude()']
        has_valid_function = any(func in response for func in valid_functions)
        
        if has_valid_function:
            score += 0.3
            details.append("✅ Contains valid OpenSCAD function")
        else:
            details.append("❌ No valid OpenSCAD function detected")
        
        # Check syntax (semicolon ending)
        if response.strip().endswith(';'):
            score += 0.2
            details.append("✅ Proper semicolon syntax")
        else:
            details.append("❌ Missing semicolon")
        
        # Check semantic correctness based on instruction
        instruction_lower = instruction.lower()
        
        if 'sphere' in instruction_lower and 'sphere(' in response:
            score += 0.5
            details.append("✅ Correct shape type (sphere)")
        elif 'cylinder' in instruction_lower and 'cylinder(' in response:
            score += 0.5  
            details.append("✅ Correct shape type (cylinder)")
        elif 'cube' in instruction_lower or 'box' in instruction_lower and 'cube(' in response:
            score += 0.5
            details.append("✅ Correct shape type (cube)")
        elif 'cone' in instruction_lower and 'cylinder(' in response and 'r1=' in response:
            score += 0.5
            details.append("✅ Correct shape type (cone)")
        elif 'torus' in instruction_lower and 'rotate_extrude' in response:
            score += 0.5
            details.append("✅ Correct shape type (torus)")
        else:
            details.append("❌ Incorrect or unrecognized shape type")
        
        return {
            "score": min(1.0, score),
            "details": details,
            "is_valid": score >= 0.7
        }
    
    def compare_models(self, instruction: str, available_models: List[str]) -> Dict:
        """Compare all available models on a single instruction"""
        print(f"\n{'='*70}")
        print(f"CAD Generation Comparison: '{instruction}'")
        print(f"{'='*70}")
        
        results = []
        
        for model in available_models:
            print(f"\nQuerying {model}...")
            result = self.query_model(model, instruction)
            results.append(result)
        
        # Display comparison table
        self.display_comparison_table(results, instruction)
        
        return {"instruction": instruction, "results": results}
    
    def display_comparison_table(self, results: List[Dict], instruction: str):
        """Display results in a formatted table"""
        print(f"\n{'Model':<15} {'Generated Code':<35} {'Status':<10} {'Score':<8} {'Time':<6}")
        print("─" * 80)
        
        best_score = 0
        best_models = []
        
        for result in results:
            if result["success"]:
                model = result["model"]
                code = result["cleaned_response"]
                validation = result.get("is_valid", self.validate_response(code, instruction))
                
                if isinstance(validation, dict):
                    score = validation["score"]
                    status = "✅ Valid" if validation["is_valid"] else "❌ Invalid"
                else:
                    score = 0.8 if validation else 0.2
                    status = "✅ Valid" if validation else "❌ Invalid"
                
                time_str = f"{result['response_time']:.1f}s"
                
                # Truncate code if too long
                display_code = code if len(code) <= 33 else code[:30] + "..."
                
                print(f"{model:<15} {display_code:<35} {status:<10} {score:.1f}/1.0   {time_str:<6}")
                
                # Track best performing models
                if score > best_score:
                    best_score = score
                    best_models = [model]
                elif score == best_score:
                    best_models.append(model)
            else:
                model = result["model"]
                error = result.get("error", "Unknown error")
                time_str = f"{result['response_time']:.1f}s"
                print(f"{model:<15} {'ERROR: ' + error:<35} {'❌ Failed':<10} {'0.0/1.0':<8} {time_str:<6}")
        
        if best_models:
            winners = ", ".join(best_models)
            print(f"\n🏆 Best Performance: {winners} (Score: {best_score:.1f}/1.0)")
        
        print("─" * 80)
    
    def interactive_mode(self):
        """Interactive model comparison mode"""
        print("\n🎯 Interactive CAD Generation Demo")
        print("="*50)
        print("Enter CAD instructions to see how different models perform.")
        print("Type 'quit' to exit, 'examples' to see sample instructions.")
        print()
        
        available_models = self.get_available_models()
        if not available_models:
            print("❌ No models available. Please install models with:")
            print("  ollama pull gemma3:1b")
            print("  ollama pull llama3")
            print("  ollama pull mistral")
            return
        
        print(f"Available models: {', '.join(available_models)}")
        
        while True:
            try:
                instruction = input("\nCAD> ").strip()
                
                if instruction.lower() in ['quit', 'exit', 'q']:
                    break
                elif instruction.lower() == 'examples':
                    self.show_examples()
                    continue
                elif not instruction:
                    continue
                
                self.compare_models(instruction, available_models)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def show_examples(self):
        """Show example instructions"""
        examples = [
            "Create a sphere radius 2.5",
            "Make a cylinder radius 3 height 8", 
            "Generate a box 5 by 2 by 10",
            "Create a cone bottom radius 4 top radius 1 height 6",
            "Make a torus major radius 8 minor radius 2"
        ]
        
        print("\n📋 Example Instructions:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
    
    def run_preset_demo(self):
        """Run a preset demo showing the key problem and solution"""
        print("🚀 CAD LLM Model Performance Showcase")
        print("="*60)
        print("Demonstrating the improvement from proper training data and model selection")
        
        available_models = self.get_available_models()
        if not available_models:
            print("❌ No models available for demo")
            return
        
        # Key test case that shows the problem
        problem_instruction = "Create a sphere radius 2.5"
        print(f"\n🎯 Problem Case: '{problem_instruction}'")
        print("Expected: sphere(r=2.5);")
        print("Gemma 3:1b often generates: cube([2.5, 2.5, 2.5]); ❌")
        
        self.compare_models(problem_instruction, available_models)
        
        # Additional test cases
        test_cases = [
            "Make a cylinder radius 3 height 8",
            "Generate a box 4 by 6 by 2"
        ]
        
        for instruction in test_cases:
            self.compare_models(instruction, available_models)
    
    def main_menu(self):
        """Main menu for the demo"""
        print("🛠️  CAD Generation Model Comparison Demo")
        print("="*50)
        
        if not self.check_ollama_connection():
            print("❌ Error: Ollama is not running!")
            print("\nPlease start Ollama:")
            print("1. Install: brew install ollama")
            print("2. Start: ollama serve")
            print("3. Download models: ollama pull gemma3:1b")
            return
        
        print("✅ Ollama connection successful")
        
        while True:
            print("\nOptions:")
            print("1. 🎯 Interactive Mode - Test any CAD instruction")
            print("2. 🚀 Preset Demo - Showcase key performance differences") 
            print("3. 📋 Show Examples - Sample CAD instructions")
            print("4. 🚪 Exit")
            
            choice = input("\nChoice (1-4): ").strip()
            
            if choice == '1':
                self.interactive_mode()
            elif choice == '2':
                self.run_preset_demo()
            elif choice == '3':
                self.show_examples()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")

def main():
    demo = CADModelDemo()
    demo.main_menu()

if __name__ == "__main__":
    main()