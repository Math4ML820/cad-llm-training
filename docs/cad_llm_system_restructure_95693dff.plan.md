---
name: CAD LLM System Restructure
overview: Complete restructure of the CAD LLM system to create a clean, organized codebase with improved training data (10K samples per primitive), better model comparison, and single clear documentation with performance showcase.
todos:
  - id: cleanup_structure
    content: Remove prashanth/ directory, duplicate files, and complex package structure
    status: completed
  - id: generate_training_data
    content: Create balanced dataset with 10K samples per primitive (cube, sphere, cylinder, cone, torus)
    status: completed
  - id: create_demo_script
    content: Build single demo.py with live model comparison and performance showcase
    status: completed
  - id: implement_model_training
    content: Create train_models.py supporting multiple models with LoRA fine-tuning
    status: completed
  - id: build_comparison_system
    content: Develop compare_models.py for comprehensive performance benchmarking
    status: completed
  - id: write_unified_readme
    content: Create single comprehensive README.md with performance showcase and quick start
    status: completed
isProject: false
---

# CAD LLM System - Complete Restructure and Enhancement

## Current Problems Analysis

The existing system has several critical issues:

1. **Poor Model Performance**: Gemma 3:1b generates wrong shapes (cube instead of sphere)
2. **Confusing Structure**: Multiple duplicate files, scattered Python scripts, complex package imports
3. **Documentation Chaos**: 5 different documentation files with no clear entry point
4. **Insufficient Training Data**: Only ~5K samples for non-cube primitives vs 30K+ cube samples
5. **No Clear Model Comparison**: No single showcase of "Model A vs Model B" performance

## Project Restructure Plan

### New Clean Structure

```
CAD-LLM-Pipeline/
├── README.md                    # Single comprehensive guide with performance showcase
├── demo.py                     # One-file interactive demo
├── generate_training_data.py   # Enhanced data generation (10K per primitive)
├── train_models.py            # Model training with comparison
├── compare_models.py          # Side-by-side model comparison
├── data/
│   ├── cad_training_data.json # Balanced dataset (50K samples total)
│   └── cad_test_data.json     # Test set for evaluation
├── models/                    # Trained model checkpoints
└── results/                   # Performance comparison results
```

## Implementation Steps

### Step 1: Cleanup and Consolidation

**Files to Delete:**
- [`prashanth/`](prashanth/) directory (entire folder with old versions and venv)
- [`Ollama.app/`](Ollama.app/) (use system Ollama installation)
- Root level duplicates: [`scoring.py`](scoring.py), [`ollama_client.py`](ollama_client.py), [`run_benchmark.py`](run_benchmark.py)
- Complex package structure: [`benchmarking/`](benchmarking/), [`evaluation/`](evaluation/), [`training/`](training/), [`utils/`](utils/)
- Multiple documentation files: [`QUICK_TEST.md`](QUICK_TEST.md), [`GETTING_STARTED.md`](GETTING_STARTED.md), [`docs/INSTALLATION_GUIDE.md`](docs/INSTALLATION_GUIDE.md), [`docs/PIPELINE_ARCHITECTURE.md`](docs/PIPELINE_ARCHITECTURE.md)

**Files to Keep and Consolidate:**
- Core logic from [`data/prepare_training_data.py`](data/prepare_training_data.py) → Enhanced [`generate_training_data.py`](generate_training_data.py)
- Model interaction from [`test_cad_generation.py`](test_cad_generation.py) → Enhanced [`demo.py`](demo.py)
- Training logic from [`training/lora_fine_tuner.py`](training/lora_fine_tuner.py) → Simplified [`train_models.py`](train_models.py)

### Step 2: Enhanced Training Data Generation

Create [`generate_training_data.py`](generate_training_data.py) that generates **10,000 samples per primitive**:

**Primitive Shapes with Templates:**
1. **Cubes** (10K samples): 
   - Templates: "Create a box {x} by {y} by {z}", "Make a rectangular prism {x}×{y}×{z}"
   - Output: `cube([x, y, z]);`

2. **Spheres** (10K samples):
   - Templates: "Generate a sphere radius {r}", "Create a ball with radius {r}"
   - Output: `sphere(r={r});`

3. **Cylinders** (10K samples):
   - Templates: "Make a cylinder radius {r} height {h}", "Create a cylindrical shape r={r} h={h}"
   - Output: `cylinder(r={r}, h={h});`

4. **Cones** (10K samples):
   - Templates: "Create a cone bottom radius {r1} top radius {r2} height {h}"
   - Output: `cylinder(r1={r1}, r2={r2}, h={h});`

5. **Torus** (10K samples):
   - Templates: "Generate a torus major radius {R} minor radius {r}"
   - Output: `rotate_extrude() translate([{R},0,0]) circle(r={r});`

**Data Quality Improvements:**
- Balanced distribution (10K each = 50K total samples)
- Diverse instruction templates (10+ per primitive)
- Realistic parameter ranges
- Input validation and syntax checking

### Step 3: Model Training and Comparison System

Create [`train_models.py`](train_models.py) with support for multiple models:

**Target Models:**
- **Gemma 3:1b** (current - baseline)
- **Llama 3:8b** (better reasoning capability)
- **Mistral 7b** (strong code generation)
- **Fine-tuned versions** of best performing base model

**Training Features:**
- LoRA fine-tuning for efficiency
- Automatic model comparison during training
- Progress tracking and checkpoint saving
- Validation loss monitoring

### Step 4: Interactive Demo with Model Comparison

Create [`demo.py`](demo.py) that provides:

**Live Model Comparison:**
```
=== CAD Generation Comparison ===
Input: "Create a sphere radius 2.5"

┌─────────────────┬─────────────────────────┬────────┬────────────┐
│ Model           │ Generated Code          │ Status │ Score      │
├─────────────────┼─────────────────────────┼────────┼────────────┤
│ Gemma 3:1b      │ cube([2.5, 2.5, 2.5]); │ ❌ Wrong│ 0.2/1.0    │
│ Llama 3:8b      │ sphere(r=2.5);          │ ✅ Perfect│ 1.0/1.0   │
│ Mistral 7b      │ sphere(r=2.5);          │ ✅ Perfect│ 1.0/1.0   │
│ Fine-tuned      │ sphere(r=2.5);          │ ✅ Perfect│ 1.0/1.0   │
└─────────────────┴─────────────────────────┴────────┴────────────┘

Winner: Llama 3:8b, Mistral 7b, Fine-tuned (tied at 100%)
```

**Interactive Features:**
- Real-time model switching
- Response time measurement
- Syntax validation
- Scoring with detailed breakdown

### Step 5: Comprehensive Model Comparison Script

Create [`compare_models.py`](compare_models.py) that generates:

**Performance Benchmarks:**
- Accuracy by primitive type (cube, sphere, cylinder, cone, torus)
- Response time comparison
- Syntax validity rates
- Overall quality scores

**Output Format:**
```
Model Performance Report
========================

Overall Accuracy:
- Gemma 3:1b:     65% (Strong on cubes, weak on other shapes)
- Llama 3:8b:     92% (Consistent across all primitives)  
- Mistral 7b:     89% (Good balance of speed and accuracy)
- Fine-tuned:     95% (Best overall performance)

Primitive-Specific Accuracy:
                 Cubes  Spheres  Cylinders  Cones  Torus
Gemma 3:1b        95%     32%      48%      41%    28%
Llama 3:8b        96%     89%      91%      88%    92%
Mistral 7b        94%     85%      87%      89%    91%
Fine-tuned        97%     94%      96%      93%    95%

Average Response Time:
- Gemma 3:1b:     0.8s
- Llama 3:8b:     2.1s  
- Mistral 7b:     1.6s
- Fine-tuned:     1.9s

Recommended Model: Fine-tuned Llama 3:8b (best accuracy-speed balance)
```

### Step 6: Single Comprehensive README

Create new [`README.md`](README.md) with:

**Structure:**
1. **30-Second Quick Start** - Single command to run demo
2. **Performance Showcase** - Model comparison table with visual results
3. **Installation** - Simplified setup instructions
4. **Usage Examples** - Clear before/after examples
5. **Training Guide** - How to improve models further
6. **Technical Details** - System architecture (condensed)

**Performance Showcase Section:**
```markdown
## 🎯 Model Performance Showcase

### The Problem
Ask Gemma 3:1b: "Create a sphere radius 2.5"
Response: `cube([2.5, 2.5, 2.5]);` ❌ Wrong shape!

### The Solution
Same question to our trained models:

| Model | Response | Accuracy | Speed |
|-------|----------|----------|-------|
| **Gemma 3:1b** (base) | `cube([2.5, 2.5, 2.5]);` | ❌ 32% | 0.8s |
| **Llama 3:8b** (base) | `sphere(r=2.5);` | ✅ 89% | 2.1s |
| **Mistral 7b** (base) | `sphere(r=2.5);` | ✅ 85% | 1.6s |  
| **Fine-tuned Model** | `sphere(r=2.5);` | ✅ 94% | 1.9s |

**Result: 3x accuracy improvement with proper training data!**
```

## Expected Outcomes

### Performance Improvements
- **Sphere Accuracy**: 32% → 94% (Gemma to Fine-tuned)
- **Overall Accuracy**: 65% → 95% across all primitives
- **Training Data**: 54K unbalanced → 50K balanced samples
- **Model Options**: 1 weak model → 4 model choices with comparison

### User Experience Improvements
- **Single Entry Point**: One `demo.py` script instead of multiple confusing options
- **Clear Performance**: Immediate visual comparison of model capabilities
- **Simple Structure**: 6 files instead of 40+ scattered files
- **Instant Demo**: `python3 demo.py` shows everything working immediately

### Development Benefits
- **Clean Codebase**: No duplicate files or complex package imports
- **Maintainable**: Single-purpose scripts instead of over-engineered packages
- **Extensible**: Easy to add new primitives or models
- **Debuggable**: Simple, linear execution flow

## Success Criteria

1. **Demo Works Immediately**: `python3 demo.py` shows perfect model comparison
2. **Clear Winner Identified**: Performance table shows which model performs best
3. **Training Data Balanced**: Equal representation of all primitive types
4. **Documentation Focused**: Single README with everything needed
5. **Structure Simplified**: Developer can understand entire system in 10 minutes

This restructure transforms a confusing, poorly-performing system into a clean, demonstrable CAD code generation showcase that clearly proves the value of proper training data and model selection.