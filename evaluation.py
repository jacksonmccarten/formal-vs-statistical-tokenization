'''
Evaluates a lexer against reference (clang) tokenizations

usage: python3 evaluate.py /path_to_lexer.py "lexer_name" /path_to_inputs /path_to_reference

Creates two folders next to the lexer:
    {lexer_name}_raw_tokenization/   -> {file_base}_tokenization_{pass}.txt
    {lexer_name}_evaluation/         -> {file_base}_score.txt
'''
import os
import sys
import time
import subprocess
from pathlib import Path
from collections import Counter

NUM_PASSES = 5


def read_tokens(path):
    with open(path, "r") as f:
        return [line for line in f.read().splitlines() if line != ""]


def accuracy(output_tokens, reference_tokens):
    # fraction of positions where the output token matches the reference token
    matches = sum(1 for o, r in zip(output_tokens, reference_tokens) if o == r)
    total = max(len(output_tokens), len(reference_tokens))
    return matches / total if total > 0 else 0.0


def f1_score(output_tokens, reference_tokens):
    # token overlap, ignoring order
    overlap = sum((Counter(output_tokens) & Counter(reference_tokens)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(output_tokens)
    recall = overlap / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def evaluation(code_path, lexer_name, input_path, reference_path):
    lexer_dir = Path(code_path).resolve().parent
    input_dir = Path(input_path)
    reference_dir = Path(reference_path)

    raw_dir = lexer_dir / f"{lexer_name}_raw_tokenization"
    eval_dir = lexer_dir / f"{lexer_name}_evaluation"
    raw_dir.mkdir(parents=True, exist_ok=True)
    eval_dir.mkdir(parents=True, exist_ok=True)

    input_files = sorted(input_dir.glob("*.c"))

    for input_file in input_files:
        reference_file = reference_dir / f"{input_file.stem}_clang_tokenization.txt"
        score_file = eval_dir / f"{input_file.stem}_score.txt"

        reference_tokens = read_tokens(reference_file)
        results = []

        for p in range(1, NUM_PASSES + 1):
            output_file = raw_dir / f"{input_file.stem}_tokenization_{p}.txt"

            start = time.perf_counter()
            process = subprocess.Popen(
                ["python3", str(code_path), str(input_file), str(output_file)]
            )
            # wait4 returns resource usage for this specific child process
            _, status, usage = os.wait4(process.pid, 0)
            runtime = time.perf_counter() - start

            if status != 0:
                raise RuntimeError(f"lexer failed on {input_file.name}")

            # peak resident memory: kilobytes on Linux, bytes on macOS
            peak_memory = usage.ru_maxrss

            output_tokens = read_tokens(output_file)
            results.append((
                p,
                peak_memory,
                runtime,
                f1_score(output_tokens, reference_tokens),
                accuracy(output_tokens, reference_tokens),
            ))

        with open(score_file, "w") as score:
            score.write(f"file: {input_file.name}\n")
            score.write(f"{'pass':<10}{'max_mem':<12}{'runtime_s':<12}{'f1':<10}{'accuracy':<10}\n")
            for p, mem, runtime, f1, acc in results:
                score.write(f"{p:<10}{mem:<12}{runtime:<12.4f}{f1:<10.4f}{acc:<10.4f}\n")

            avg_mem = sum(r[1] for r in results) / len(results)
            avg_runtime = sum(r[2] for r in results) / len(results)
            avg_f1 = sum(r[3] for r in results) / len(results)
            avg_acc = sum(r[4] for r in results) / len(results)
            score.write(f"{'average':<10}{avg_mem:<12.1f}{avg_runtime:<12.4f}{avg_f1:<10.4f}{avg_acc:<10.4f}\n")


def main():
    code_path = sys.argv[1]
    lexer_name = sys.argv[2]
    input_path = sys.argv[3]
    reference_path = sys.argv[4]
    evaluation(code_path, lexer_name, input_path, reference_path)


if __name__ == "__main__":
    main()