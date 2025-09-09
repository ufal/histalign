import json
import argparse

def normalize_ids(entry):
    def split_ids(val):
        if isinstance(val, str):
            return [v.strip() for v in val.split(',') if v.strip()]
        return val if isinstance(val, list) else []
    entry["id1"] = split_ids(entry.get("id1", []))
    entry["id2"] = split_ids(entry.get("id2", []))
    return entry

def load_alignments(filename):
    with open(filename, "r", encoding="utf-8") as f:
        full = json.load(f)
        data = full['sentences']
    return [normalize_ids(e) for e in data]

def extract_links(alignments):
    return set((s, t) for a in alignments for s in a["id1"] for t in a["id2"])

def extract_sure_links(alignments):
    # Optionally, if you have "sure" vs. "possible", implement here
    return extract_links(alignments)

def compute_aer(gold, auto):
    A = extract_links(auto)
    S = extract_sure_links(gold)
    P = extract_links(gold)

    if not A and not S:
        return 0.0  # Avoid division by zero if both are empty

    num_A = len(A)
    num_S = len(S)
    num_intersect_AS = len(A & S)
    num_intersect_AP = len(A & P)

    aer = 1 - (num_intersect_AS + num_intersect_AP) / (num_A + num_S)
    return aer

parser = argparse.ArgumentParser(description="Align TEI/XML sentences using Hunalign.")
parser.add_argument('file1', type=str, help='Path to the first file (witness A)')
parser.add_argument('file2', type=str, help='Path to the second file (witness B)')
parser.add_argument('--output', type=str, help='Output filename', )

args = parser.parse_args()

# Load files
gold = load_alignments(args.file1)
auto = load_alignments(args.file2)

aer = compute_aer(auto, gold)
print(f"Alignment Error Rate (AER): {aer:.3f}")
