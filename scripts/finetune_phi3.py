"""
scripts/finetune_phi3.py
Fine-tune Microsoft Phi-3-mini on ECE lab QA pairs using LoRA.

Run this on Google Colab (free T4 GPU, ~2-3 hours for full dataset):
  1. Upload this file and training_pairs.jsonl to Colab
  2. pip install transformers peft datasets bitsandbytes trl accelerate
  3. python finetune_phi3.py

The fine-tuned model will be saved and can be loaded with Ollama or
directly via transformers for completely offline inference.
"""

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME    = "microsoft/Phi-3-mini-4k-instruct"
DATA_PATH     = "training_pairs.jsonl"          # upload this to Colab
OUTPUT_DIR    = "./phi3_ece_lora"
MAX_SEQ_LEN   = 512
BATCH_SIZE    = 4
GRAD_ACCUM    = 4                               # effective batch = 16
EPOCHS        = 3
LR            = 2e-4
LORA_R        = 16
LORA_ALPHA    = 32
LORA_DROPOUT  = 0.05


# ── Load and format data ───────────────────────────────────────────────────────
def format_prompt(example: dict) -> str:
    """Phi-3 instruction format."""
    instruction = example["instruction"]
    context     = example.get("input", "")
    response    = example["output"]

    if context:
        user_msg = f"{instruction}\n\nContext: {context}"
    else:
        user_msg = instruction

    return (
        f"<|user|>\n{user_msg}<|end|>\n"
        f"<|assistant|>\n{response}<|end|>"
    )


def load_dataset(path: str) -> Dataset:
    pairs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))

    formatted = [{"text": format_prompt(p)} for p in pairs]
    print(f"Loaded {len(formatted)} training samples")
    return Dataset.from_list(formatted)


# ── Main fine-tuning ──────────────────────────────────────────────────────────
def main():
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # 4-bit quantization for Colab T4 (reduces VRAM from ~8GB to ~4GB)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"\nLoading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA config — only trains ~1% of parameters
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load dataset
    dataset = load_dataset(DATA_PATH)
    # 90/10 train/val split
    split   = dataset.train_test_split(test_size=0.1, seed=42)
    train_d = split["train"]
    val_d   = split["test"]
    print(f"Train: {len(train_d)}, Val: {len(val_d)}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=True,
        logging_steps=20,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=2,
        report_to="none",
        dataloader_num_workers=2,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_d,
        eval_dataset=val_d,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LEN,
        tokenizer=tokenizer,
    )

    print("\nStarting fine-tuning...")
    trainer.train()

    # Save LoRA adapter
    adapter_path = os.path.join(OUTPUT_DIR, "final_adapter")
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    print(f"\nLoRA adapter saved to: {adapter_path}")
    print("Upload this folder to your server and use with Ollama or transformers.")

    # Quick inference test
    print("\n── Inference test ──────────────────────────────")
    model.eval()
    test_questions = [
        "In the CE amplifier experiment, output is clipping. What is wrong?",
        "What is the formula for cutoff frequency in RC filter?",
        "What happens if the Zener diode is connected in forward bias in a regulator?",
    ]
    for q in test_questions:
        prompt = f"<|user|>\n{q}<|end|>\n<|assistant|>\n"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"\nQ: {q}")
        print(f"A: {response}")


if __name__ == "__main__":
    main()


# ══════════════════════════════════════════════════════════════════════════════
# COLAB SETUP COMMANDS (paste in a Colab cell before running this script):
# ══════════════════════════════════════════════════════════════════════════════
"""
!pip install -q transformers peft datasets bitsandbytes trl accelerate sentencepiece
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Upload training_pairs.jsonl and this script to Colab, then:
!python finetune_phi3.py

# After training, download the adapter:
from google.colab import files
import shutil
shutil.make_archive('phi3_ece_adapter', 'zip', './phi3_ece_lora/final_adapter')
files.download('phi3_ece_adapter.zip')

# To use the fine-tuned model locally with Ollama:
# 1. Convert LoRA adapter to GGUF format (use llama.cpp)
# 2. Create Modelfile: FROM phi3:mini  ADAPTER ./phi3_ece_adapter.gguf
# 3. ollama create ece-assistant -f Modelfile
# 4. Set OLLAMA_MODEL=ece-assistant in your .env
"""
