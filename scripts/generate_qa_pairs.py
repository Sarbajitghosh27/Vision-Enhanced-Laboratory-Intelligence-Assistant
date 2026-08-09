"""
scripts/generate_qa_pairs.py
Converts all experiment JSONs into training QA pairs for Phi-3 fine-tuning.

Run: python scripts/generate_qa_pairs.py
Output: data/qa_pairs/training_pairs.jsonl  (Alpaca format for LoRA)

Generates ~60-80 QA pairs per experiment:
  - Theory questions (concept explanation)
  - Procedure questions (step by step)
  - Diagnosis questions (fault → cause → fix)
  - Viva questions (from the viva_questions field)
  - Formula application questions
  - Component identification questions
"""

import os
import json
import glob
import random

DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "experiments")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "qa_pairs", "training_pairs.jsonl")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

random.seed(42)


def alpaca(instruction: str, response: str, context: str = "") -> dict:
    """Alpaca format — what LoRA fine-tuning expects."""
    return {
        "instruction": instruction,
        "input":       context,
        "output":      response,
    }


def generate_pairs_for_experiment(exp: dict) -> list[dict]:
    pairs = []
    title  = exp["title"]
    aim    = exp["aim"]
    theory = exp.get("theory", {})
    sem    = exp.get("semester")
    lab    = exp.get("lab_code")

    # ── 1. Theory / concept questions ─────────────────────────────────────
    pairs.append(alpaca(
        f"What is the aim of the {title} experiment?",
        aim,
    ))

    pairs.append(alpaca(
        f"Explain the theory behind {title} in simple terms.",
        theory.get("summary", ""),
    ))

    pairs.append(alpaca(
        f"What are the key concepts in the {title} experiment?",
        "The key concepts include: " + ", ".join(theory.get("key_concepts", [])) + ".",
    ))

    # ── 2. Formula questions ───────────────────────────────────────────────
    for f in theory.get("key_formulas", []):
        pairs.append(alpaca(
            f"What is the formula for {f['name']} in the {title} experiment?",
            f"The formula is: {f['formula']}. Where {f.get('variables', '')}.",
        ))
        # Application variant
        pairs.append(alpaca(
            f"How do you calculate {f['name']}?",
            f"{f['formula']}. {f.get('variables', '')}",
            context=f"Experiment: {title}",
        ))

    # ── 3. Procedure questions ─────────────────────────────────────────────
    procedure = exp.get("procedure", [])
    if procedure:
        pairs.append(alpaca(
            f"What are the steps to perform the {title} experiment?",
            "\n".join(procedure),
        ))
        pairs.append(alpaca(
            f"How do I start the {title} experiment?",
            procedure[0] if procedure else "",
        ))
        if len(procedure) > 1:
            pairs.append(alpaca(
                f"What is the last step of the {title} experiment?",
                procedure[-1],
            ))

    # ── 4. Components questions ────────────────────────────────────────────
    components = exp.get("components", [])
    if components:
        comp_list = ", ".join(
            f"{c['name']} ({c.get('spec', '')})" for c in components
        )
        pairs.append(alpaca(
            f"What components are needed for the {title} experiment?",
            f"You will need: {comp_list}.",
        ))
        # Individual component questions
        for comp in components:
            if comp.get("spec"):
                pairs.append(alpaca(
                    f"What specification of {comp['name']} is used in {title}?",
                    f"{comp['name']} with specification: {comp['spec']}, quantity: {comp.get('quantity', 1)}.",
                    context=f"Experiment: {title}",
                ))

    # ── 5. Fault diagnosis questions ───────────────────────────────────────
    for err in exp.get("common_errors", []):
        symptom = err.get("symptom", "")
        causes  = ", ".join(err.get("causes", []))
        fix     = err.get("fix", "")

        # Student-style query variants
        student_queries = [
            f"In the {title} experiment, {symptom.lower()}. What is wrong?",
            f"My {title} circuit shows: {symptom}. How do I fix it?",
            f"I am getting this problem in {title}: {symptom}. What should I check?",
            f"Why does {symptom.lower()} happen in the {title} experiment?",
        ]
        answer = (
            f"Possible causes: {causes}.\n"
            f"How to fix: {fix}"
        )
        for q in student_queries:
            pairs.append(alpaca(q, answer))

    # ── 6. Circuit diagnosis hints ─────────────────────────────────────────
    for hint in exp.get("circuit_diagnosis_hints", []):
        pairs.append(alpaca(
            f"Give a circuit inspection tip for the {title} experiment.",
            hint,
        ))

    # ── 7. Viva questions ──────────────────────────────────────────────────
    for viva in exp.get("viva_questions", []):
        q = viva.get("q", "")
        a = viva.get("a", "")
        if q and a:
            pairs.append(alpaca(q, a))
            # Rephrase variant
            pairs.append(alpaca(
                f"For the {title} experiment viva: {q}",
                a,
            ))

    # ── 8. Expected results questions ─────────────────────────────────────
    exp_results = exp.get("expected_results", {})
    desc = exp_results.get("description", "")
    if desc:
        pairs.append(alpaca(
            f"What results should I expect from the {title} experiment?",
            desc,
        ))
    for tv in exp_results.get("typical_values", []):
        pairs.append(alpaca(
            f"What is the typical value of {tv['parameter']} in {title}?",
            f"Typical {tv['parameter']}: {tv['expected']} {tv.get('unit', '')}.",
            context=f"Experiment: {title}",
        ))

    # ── 9. Observation table questions ────────────────────────────────────
    obs = exp.get("observations", {})
    if obs.get("what_to_plot"):
        pairs.append(alpaca(
            f"What graph should I plot for the {title} experiment?",
            obs["what_to_plot"],
        ))
    if obs.get("table_headers"):
        pairs.append(alpaca(
            f"What columns should the observation table have for {title}?",
            "Observation table columns: " + ", ".join(obs["table_headers"]) + ".",
        ))

    # ── 10. Semester / lab identification ─────────────────────────────────
    pairs.append(alpaca(
        f"Which semester and lab does the {title} experiment belong to?",
        f"This experiment is from Semester {sem}, {lab} — {exp.get('lab_name', '')}.",
    ))

    # Reverse lookup
    pairs.append(alpaca(
        f"List the experiments in semester {sem} {lab}.",
        f"One of the experiments is: {title} — {aim}",
        context=f"Semester {sem}, {lab}",
    ))

    return pairs


def main():
    all_pairs = []

    experiment_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    if not experiment_files:
        print(f"No JSON files found in {DATA_DIR}")
        return

    for path in experiment_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        experiments = data if isinstance(data, list) else [data]

        for exp in experiments:
            pairs = generate_pairs_for_experiment(exp)
            all_pairs.extend(pairs)
            print(f"  {exp['id']:50s}  {len(pairs):3d} pairs")

    # Shuffle for training
    random.shuffle(all_pairs)

    # Write JSONL
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair) + "\n")

    print(f"\nTotal QA pairs: {len(all_pairs)}")
    print(f"Saved to: {OUT_PATH}")
    print("\nSample pair:")
    sample = random.choice(all_pairs)
    print(json.dumps(sample, indent=2))

    # Also save as JSON array (for inspection)
    json_path = OUT_PATH.replace(".jsonl", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_pairs, f, indent=2)
    print(f"\nAlso saved JSON array to: {json_path}")


if __name__ == "__main__":
    main()
