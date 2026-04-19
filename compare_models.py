#!/usr/bin/env python3
"""
Comprehensive Model Comparison for CAD Generation

Generates detailed performance benchmarks across multiple models:
- Accuracy by primitive type
- Response time analysis 
- Syntax validity rates
- Overall quality scores
"""

import json
import time
import requests
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class CADModelComparator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.test_data_file = "data/cad_test_data.json"
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Models to compare
        self.models = {
            "gemma3:1b": "Gemma 3 (1B)",
            "llama3": "Llama 3 (8B)", 
            "mistral": "Mistral (7B)"
        }
        
        self.system_prompt = """You are an expert OpenSCAD code generator. Generate ONLY valid OpenSCAD code without explanations.

Rules:
1. Output only the code, no markdown or explanations
2. End statements with semicolons
3. Use exact syntax:
   - Cubes: cube([x, y, z]);
   - Spheres: sphere(r=radius);
   - Cylinders: cylinder(r=radius, h=height);
   - Cones: cylinder(r1=r1, r2=r2, h=height);
   - Torus: rotate_extrude() translate([R,0,0]) circle(r=r);"""

    def load_test_data(self) -> List[Dict]:
        """Load test dataset"""
        with open(self.test_data_file, 'r') as f:
            data = json.load(f)
        
        # Use a subset for manageable evaluation
        return data[:500]  # 500 test samples
    
    def check_ollama_models(self) -> List[str]:
        """Check which models are available in Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return []
            
            models_data = response.json()
            available = []
            
            for model in models_data.get('models', []):
                model_name = model['name']
                for known_model in self.models.keys():
                    if known_model in model_name:
                        available.append(known_model)
                        break
            
            return list(set(available))  # Remove duplicates
        except:
            return []
    
    def query_model(self, model: str, instruction: str) -> Dict:
        """Query model with instruction and measure performance"""
        full_prompt = f"{self.system_prompt}\n\nInput: {instruction}\nOutput:"
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                raw_output = response.json()["response"]
                cleaned_output = self.clean_response(raw_output)
                
                return {
                    "success": True,
                    "raw_output": raw_output,
                    "cleaned_output": cleaned_output,
                    "response_time": response_time
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def clean_response(self, response: str) -> str:
        """Clean response to extract OpenSCAD code"""
        import re
        
        # Remove markdown
        response = re.sub(r'```[a-zA-Z]*\n', '', response)
        response = re.sub(r'```', '', response)
        
        # Look for lines with OpenSCAD functions
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if any(func in line for func in ['cube(', 'cylinder(', 'sphere(', 'rotate_extrude(']):
                if not line.endswith(';'):
                    line += ';'
                return line
        
        # Return cleaned response if no obvious code found
        return response.strip()
    
    def evaluate_response(self, predicted: str, expected: str, instruction: str) -> Dict:
        """Evaluate prediction against expected output"""
        scores = {}
        
        # 1. Exact match
        scores['exact_match'] = 1.0 if predicted.strip() == expected.strip() else 0.0
        
        # 2. Syntax validity (ends with semicolon, has function)
        has_semicolon = predicted.strip().endswith(';')
        has_function = any(func in predicted for func in ['cube(', 'cylinder(', 'sphere(', 'rotate_extrude('])
        scores['syntax_valid'] = 1.0 if (has_semicolon and has_function) else 0.0
        
        # 3. Shape type correctness
        instruction_lower = instruction.lower()
        shape_correct = False
        
        if 'sphere' in instruction_lower:
            shape_correct = 'sphere(' in predicted
        elif 'cylinder' in instruction_lower and 'cone' not in instruction_lower:
            shape_correct = 'cylinder(' in predicted and 'r1=' not in predicted
        elif 'cube' in instruction_lower or 'box' in instruction_lower:
            shape_correct = 'cube(' in predicted
        elif 'cone' in instruction_lower:
            shape_correct = 'cylinder(' in predicted and 'r1=' in predicted
        elif 'torus' in instruction_lower or 'donut' in instruction_lower:
            shape_correct = 'rotate_extrude(' in predicted
        
        scores['shape_correct'] = 1.0 if shape_correct else 0.0
        
        # 4. Parameter extraction accuracy (simplified)
        import re
        
        # Extract numbers from both strings
        predicted_nums = re.findall(r'\d+\.?\d*', predicted)
        expected_nums = re.findall(r'\d+\.?\d*', expected)
        
        param_accuracy = 0.0
        if len(predicted_nums) == len(expected_nums):
            matches = 0
            for p_num, e_num in zip(predicted_nums, expected_nums):
                if abs(float(p_num) - float(e_num)) < 0.01:
                    matches += 1
            param_accuracy = matches / len(expected_nums) if expected_nums else 0.0
        
        scores['parameter_accuracy'] = param_accuracy
        
        # 5. Overall score (weighted)
        overall = (
            scores['exact_match'] * 0.4 +
            scores['shape_correct'] * 0.3 +
            scores['syntax_valid'] * 0.2 +
            scores['parameter_accuracy'] * 0.1
        )
        
        scores['overall'] = overall
        
        return scores
    
    def classify_primitive(self, instruction: str) -> str:
        """Classify instruction by primitive type"""
        instruction_lower = instruction.lower()
        
        if 'sphere' in instruction_lower or 'ball' in instruction_lower:
            return 'sphere'
        elif 'cylinder' in instruction_lower and 'cone' not in instruction_lower:
            return 'cylinder'
        elif 'cube' in instruction_lower or 'box' in instruction_lower:
            return 'cube'
        elif 'cone' in instruction_lower:
            return 'cone'
        elif 'torus' in instruction_lower or 'donut' in instruction_lower:
            return 'torus'
        else:
            return 'unknown'
    
    def benchmark_model(self, model: str, test_data: List[Dict]) -> Dict:
        """Benchmark a single model on test data"""
        print(f"Benchmarking {self.models.get(model, model)}...")
        
        results = {
            'model': model,
            'total_samples': len(test_data),
            'successful_responses': 0,
            'failed_responses': 0,
            'response_times': [],
            'scores_by_primitive': defaultdict(list),
            'overall_scores': [],
            'detailed_results': []
        }
        
        for i, sample in enumerate(test_data):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(test_data)}")
            
            instruction = sample['instruction']
            expected = sample['output']
            primitive = self.classify_primitive(instruction)
            
            # Query model
            response = self.query_model(model, instruction)
            
            if response['success']:
                results['successful_responses'] += 1
                results['response_times'].append(response['response_time'])
                
                # Evaluate response
                scores = self.evaluate_response(response['cleaned_output'], expected, instruction)
                results['overall_scores'].append(scores['overall'])
                results['scores_by_primitive'][primitive].append(scores['overall'])
                
                # Store detailed result
                results['detailed_results'].append({
                    'instruction': instruction,
                    'expected': expected,
                    'predicted': response['cleaned_output'],
                    'primitive': primitive,
                    'scores': scores,
                    'response_time': response['response_time']
                })
            else:
                results['failed_responses'] += 1
                results['detailed_results'].append({
                    'instruction': instruction,
                    'expected': expected,
                    'predicted': '',
                    'primitive': primitive,
                    'error': response.get('error', 'Unknown error'),
                    'response_time': response['response_time']
                })
        
        # Calculate summary statistics
        if results['overall_scores']:
            results['mean_accuracy'] = statistics.mean(results['overall_scores'])
            results['median_accuracy'] = statistics.median(results['overall_scores'])
        else:
            results['mean_accuracy'] = 0.0
            results['median_accuracy'] = 0.0
        
        if results['response_times']:
            results['mean_response_time'] = statistics.mean(results['response_times'])
            results['median_response_time'] = statistics.median(results['response_times'])
        else:
            results['mean_response_time'] = 0.0
            results['median_response_time'] = 0.0
        
        # Calculate primitive-specific accuracies
        results['primitive_accuracies'] = {}
        for primitive, scores in results['scores_by_primitive'].items():
            if scores:
                results['primitive_accuracies'][primitive] = statistics.mean(scores)
        
        return results
    
    def generate_comparison_report(self, all_results: Dict[str, Dict]) -> str:
        """Generate comprehensive comparison report"""
        
        report = []
        report.append("CAD Model Performance Report")
        report.append("="*50)
        report.append("")
        
        # Overall accuracy comparison
        report.append("Overall Accuracy:")
        accuracies = []
        for model, results in all_results.items():
            accuracy = results['mean_accuracy'] * 100
            model_name = self.models.get(model, model)
            report.append(f"- {model_name:<20} {accuracy:.1f}%")
            accuracies.append((model_name, accuracy))
        
        # Find best performing model
        best_model = max(accuracies, key=lambda x: x[1])
        report.append(f"\n🏆 Best Overall: {best_model[0]} ({best_model[1]:.1f}%)")
        report.append("")
        
        # Primitive-specific comparison
        report.append("Primitive-Specific Accuracy:")
        primitives = ['cube', 'sphere', 'cylinder', 'cone', 'torus']
        
        # Header
        header = f"{'Model':<20}"
        for prim in primitives:
            header += f"{prim.capitalize():<12}"
        report.append(header)
        report.append("-" * 80)
        
        # Data rows
        for model, results in all_results.items():
            model_name = self.models.get(model, model)
            row = f"{model_name:<20}"
            for prim in primitives:
                accuracy = results['primitive_accuracies'].get(prim, 0) * 100
                row += f"{accuracy:<12.1f}"
            report.append(row)
        
        report.append("")
        
        # Response time comparison
        report.append("Average Response Time:")
        times = []
        for model, results in all_results.items():
            time_val = results['mean_response_time']
            model_name = self.models.get(model, model)
            report.append(f"- {model_name:<20} {time_val:.2f}s")
            times.append((model_name, time_val))
        
        fastest_model = min(times, key=lambda x: x[1])
        report.append(f"\n⚡ Fastest: {fastest_model[0]} ({fastest_model[1]:.2f}s)")
        report.append("")
        
        # Success rates
        report.append("Success Rate (Non-failed responses):")
        for model, results in all_results.items():
            success_rate = (results['successful_responses'] / results['total_samples']) * 100
            model_name = self.models.get(model, model)
            report.append(f"- {model_name:<20} {success_rate:.1f}%")
        
        report.append("")
        
        # Recommendations
        report.append("Recommendations:")
        
        # Find best accuracy-speed balance
        balance_scores = []
        for model, results in all_results.items():
            accuracy = results['mean_accuracy']
            speed_score = 1.0 / (results['mean_response_time'] + 0.1)  # Avoid division by zero
            balance = (accuracy * 0.7) + (speed_score * 0.3)  # Weight accuracy more
            balance_scores.append((self.models.get(model, model), balance, accuracy, results['mean_response_time']))
        
        balance_scores.sort(key=lambda x: x[1], reverse=True)
        
        report.append(f"- Best Overall Performance: {balance_scores[0][0]}")
        report.append(f"- Best Accuracy: {best_model[0]} ({best_model[1]:.1f}%)")
        report.append(f"- Fastest Response: {fastest_model[0]} ({fastest_model[1]:.2f}s)")
        
        return "\n".join(report)
    
    def run_comparison(self):
        """Run complete model comparison"""
        print("="*60)
        print("CAD MODEL PERFORMANCE COMPARISON")
        print("="*60)
        
        # Check Ollama connection
        try:
            requests.get(f"{self.ollama_url}/api/tags", timeout=5)
        except:
            print("❌ Error: Ollama is not running!")
            print("Please start Ollama: ollama serve")
            return
        
        # Get available models
        available_models = self.check_ollama_models()
        if not available_models:
            print("❌ No supported models found in Ollama")
            print("Install models with: ollama pull gemma3:1b")
            return
        
        print(f"Available models: {', '.join([self.models[m] for m in available_models])}")
        
        # Load test data
        test_data = self.load_test_data()
        print(f"Loaded {len(test_data)} test samples")
        
        # Benchmark each model
        all_results = {}
        for model in available_models:
            results = self.benchmark_model(model, test_data)
            all_results[model] = results
            
            # Save individual results
            results_file = self.results_dir / f"{model.replace(':', '_')}_benchmark.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ {self.models[model]} completed")
        
        # Generate and save comparison report
        report = self.generate_comparison_report(all_results)
        report_file = self.results_dir / "model_comparison_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print("\n" + "="*60)
        print("COMPARISON COMPLETE!")
        print("="*60)
        print(report)
        print(f"\n📊 Detailed results saved in: {self.results_dir}/")

def main():
    comparator = CADModelComparator()
    comparator.run_comparison()

if __name__ == "__main__":
    main()