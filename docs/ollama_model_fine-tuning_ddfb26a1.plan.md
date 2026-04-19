---
name: Ollama Model Fine-tuning
overview: Modify the training script to export Ollama models (gemma3:1b, llama3, mistral) to HuggingFace format, fine-tune them with LoRA using the CAD training data, and import them back to Ollama as specialized CAD models.
todos:
  - id: setup_virtual_env
    content: Create virtual environment and install required ML dependencies
    status: pending
  - id: implement_ollama_exporter
    content: Add OllamaModelExporter class to handle model export/import
    status: pending
  - id: update_trainable_models
    content: Replace GPT-2 models with Ollama model configurations
    status: pending
  - id: enhance_lora_training
    content: Update LoRA training with model-specific configurations
    status: pending
  - id: implement_model_import
    content: Add functionality to import fine-tuned models back to Ollama
    status: pending
  - id: update_demo_comparison
    content: Modify demo and comparison scripts to include fine-tuned models
    status: pending
isProject: false
---

# Ollama Model Fine-tuning Implementation

## Current Situation Analysis

The existing [`train_models.py`](train_models.py) trains GPT-2 models from HuggingFace, but you want to fine-tune your Ollama models:
- `gemma3:1b` (815 MB)
- `llama3:latest` (4.7 GB) 
- `mistral:latest` (4.4 GB)

## Implementation Approach

### Step 1: Environment Setup with Virtual Environment

Create a clean Python environment to avoid the "externally managed environment" error:

```bash
python3 -m venv cad_training_env
source cad_training_env/bin/activate
pip install torch transformers datasets peft accelerate ollama-python
```

This resolves the pip installation errors you encountered.

### Step 2: Ollama Model Export System

Modify [`train_models.py`](train_models.py) to include an `OllamaModelExporter` class:

**Key Components:**
- **Model Discovery**: Query Ollama API to find available models
- **GGUF to HuggingFace Conversion**: Export models using `transformers` library
- **Model Mapping**: Handle the conversion between Ollama model names and HuggingFace equivalents

**Technical Implementation:**
```python
class OllamaModelExporter:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.export_dir = Path("exported_models")
        
    def list_ollama_models(self):
        # Query Ollama API for available models
        
    def export_model(self, ollama_name: str, hf_path: str):
        # Convert GGUF format to HuggingFace format
        
    def import_model_to_ollama(self, hf_path: str, new_ollama_name: str):
        # Create Ollama Modelfile and import trained model
```

### Step 3: Enhanced Training Pipeline

Replace the existing `trainable_models` dictionary in [`train_models.py`](train_models.py) with your Ollama models:

**Before:**
```python
self.trainable_models = {
    "gpt2": {"model_name": "gpt2", ...},
    "distilgpt2": {"model_name": "distilgpt2", ...}
}
```

**After:**
```python
self.trainable_models = {
    "gemma3-1b": {
        "ollama_name": "gemma3:1b",
        "hf_equivalent": "google/gemma-2b-it",
        "max_length": 256,
        "batch_size": 2,
        "learning_rate": 1e-4
    },
    "llama3": {
        "ollama_name": "llama3:latest", 
        "hf_equivalent": "meta-llama/Meta-Llama-3-8B",
        "max_length": 512,
        "batch_size": 1,
        "learning_rate": 5e-5
    },
    "mistral": {
        "ollama_name": "mistral:latest",
        "hf_equivalent": "mistralai/Mistral-7B-v0.1", 
        "max_length": 512,
        "batch_size": 1,
        "learning_rate": 5e-5
    }
}
```

### Step 4: LoRA Fine-tuning Configuration

Update the `real_lora_training` method in [`train_models.py`](train_models.py) with model-specific LoRA configurations:

**Gemma 3:1b Configuration:**
- Target modules: `["q_proj", "k_proj", "v_proj", "o_proj"]`
- LoRA rank: 16
- LoRA alpha: 32
- Dropout: 0.1

**Llama 3 Configuration:**
- Target modules: `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
- LoRA rank: 64
- LoRA alpha: 16
- Dropout: 0.05

**Mistral Configuration:**
- Target modules: `["q_proj", "k_proj", "v_proj", "o_proj"]`
- LoRA rank: 32
- LoRA alpha: 64
- Dropout: 0.1

### Step 5: Training Data Integration

Utilize the existing balanced CAD dataset from [`data/cad_training_data.json`](data/cad_training_data.json):
- 45,000 training samples (9,000 per primitive type)
- 5,000 test samples (1,000 per primitive type)
- Balanced distribution: cubes, spheres, cylinders, cones, torus

**Data Preprocessing:**
- Format as instruction-response pairs for each model's chat template
- Add model-specific system prompts for CAD generation
- Tokenize with appropriate max_length for each model

### Step 6: Model Import Back to Ollama

Create new Ollama models with fine-tuned weights:

**Ollama Modelfile Template:**
```
FROM ./fine_tuned_model_path
TEMPLATE """<|system|>
You are an expert OpenSCAD code generator specialized in CAD design.
<|user|>
{{ .Prompt }}
<|assistant|>
"""
PARAMETER temperature 0.1
PARAMETER top_p 0.9
```

**New Model Names:**
- `gemma3-cad:1b` (fine-tuned Gemma)
- `llama3-cad:8b` (fine-tuned Llama)  
- `mistral-cad:7b` (fine-tuned Mistral)

### Step 7: Demo and Comparison Integration

Update [`demo.py`](demo.py) and [`compare_models.py`](compare_models.py) to include both base and fine-tuned models:

**Extended Model Dictionary:**
```python
self.models = {
    # Base models
    "gemma": "gemma3:1b",
    "llama": "llama3", 
    "mistral": "mistral",
    # Fine-tuned models
    "gemma-cad": "gemma3-cad:1b",
    "llama-cad": "llama3-cad:8b", 
    "mistral-cad": "mistral-cad:7b"
}
```

This enables direct before/after comparison showing the improvement from fine-tuning.

## Expected Workflow

### Training Process:
1. **Setup Environment**: `python3 -m venv cad_training_env && source cad_training_env/bin/activate`
2. **Export Models**: `python3 train_models.py --export-ollama-models`
3. **Train Models**: `python3 train_models.py --model all`
4. **Import to Ollama**: `python3 train_models.py --import-to-ollama`

### Demonstration:
1. **Base vs Fine-tuned Demo**: `python3 demo.py` (shows 6 models total)
2. **Comprehensive Comparison**: `python3 compare_models.py` (benchmarks all models)

## Technical Challenges and Solutions

### Challenge 1: Model Format Conversion
**Solution**: Use `transformers` library's `from_pretrained` with local GGUF files and `save_pretrained` for HuggingFace format.

### Challenge 2: Large Model Memory Requirements  
**Solution**: 
- Use 4-bit quantization during training
- Gradient checkpointing to reduce memory usage
- Batch size of 1 for larger models (Llama, Mistral)

### Challenge 3: Ollama Model Import
**Solution**: Create Ollama Modelfiles that reference the fine-tuned HuggingFace models and use `ollama create` command.

## Success Metrics

### Training Success:
- All 3 models export successfully from Ollama
- LoRA training completes without memory errors
- Fine-tuned models import back to Ollama successfully

### Performance Success:
- Fine-tuned models show >20% accuracy improvement on CAD generation
- Sphere generation accuracy improves from 32% to >80% 
- Demo shows clear before/after performance difference

## Files to Modify

1. **[`train_models.py`](train_models.py)**: Complete rewrite with Ollama integration
2. **[`demo.py`](demo.py)**: Add fine-tuned model options  
3. **[`compare_models.py`](compare_models.py)**: Include base vs fine-tuned comparison
4. **[`README.md`](README.md)**: Update with new training workflow

## Resource Requirements

### Disk Space:
- Exported models: ~15 GB (original model files)
- Fine-tuned adapters: ~2 GB (LoRA weights)
- Training cache: ~5 GB

### Memory:
- Gemma 3:1b training: ~4 GB RAM
- Llama 3:8b training: ~12 GB RAM  
- Mistral 7b training: ~10 GB RAM

### Training Time (CPU):
- Gemma: ~2 hours
- Llama: ~8 hours
- Mistral: ~6 hours