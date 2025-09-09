import subprocess
import tempfile
import lxml.etree as ET
import os
import json
import argparse
import shutil

def extract_sentences(tei_file):
    """Extracts sentences and their IDs from a TEI XML file."""
    tree = ET.parse(tei_file)
    root = tree.getroot()

    # Remove all <note> fields
    for note in root.findall('.//note'):
        parent = note.getparent()
        if parent is not None:
            parent.remove(note)   
            
    sentences = []
    
    for s in root.xpath('//text//s' ):
        sent_id = s.get("id", f"sent_{len(sentences) + 1}")  # Default ID if missing
        text = "".join(s.itertext()).strip().replace("\n", " ")
        if text:
            sentences.append((sent_id, text))
    
    return sentences

def write_temp_file(sentences):
    """Writes sentences to a temporary file and returns the file path."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
    for _, sentence in sentences:
        temp_file.write(sentence + "\n")
    temp_file.close()
    return temp_file.name

def run_hunalign(src_file, tgt_file, dictionary=None):
    """Runs Hunalign to align sentences between source and target files."""
    aligned_output = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
    
    hunalign_cmd = ["hunalign", "-text", dictionary if dictionary else "/dev/null", src_file, tgt_file]
    try:
        result = subprocess.run(hunalign_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        aligned_output.write(result.stdout)
        aligned_output.close()
    except Exception as e:
        print(f"Error running Hunalign: {e}")
        return None

    return aligned_output.name

def parse_alignment(alignment_file, src_sentences, tgt_sentences):
    """Parses Hunalign output and matches sentence IDs."""
    with open(alignment_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    aligned_pairs = []
    for i, line in enumerate(lines):
        parts = line.replace("\n", "").split("\t")
        # print(parts)
        if len(parts) < 2:
            print("Skipping")
            continue
        src_text, tgt_text = parts[:2]

        # Find the original IDs
        # src_id = next((s_id for s_id, s_text in src_sentences if s_text == src_text), f"src_{i+1}")
        # tgt_id = next((t_id for t_id, t_text in tgt_sentences if t_text == tgt_text), f"tgt_{i+1}")
        
        src_id = ''
        sep = ''
        if src_text != '':
            for src_part in src_text.split('~~~'):
                sent = src_sentences.pop(0)
                src_id = src_id + sep + sent[0]
                sep = ','
            
        tgt_id = ''
        sep = ''
        if tgt_text != '':
            for tgt_part in tgt_text.split('~~~'):
                sent = tgt_sentences.pop(0)
                tgt_id = tgt_id + sep + sent[0]
                sep = ','

        aligned_pairs.append({"id1": src_id, "text1": src_text, "id2": tgt_id, "text2": tgt_text})

    return aligned_pairs

def main(src_tei, tgt_tei, output_json, dictionary=None):
    """Main function to align TEI/XML files and save output as JSON."""
    src_sentences = extract_sentences(src_tei)
    tgt_sentences = extract_sentences(tgt_tei)

    # print(src_sentences)

    src_file = write_temp_file(src_sentences)
    tgt_file = write_temp_file(tgt_sentences)
    
    shutil.copy(src_file, "tmp/src.txt")
    shutil.copy(tgt_file, "tmp/tgt.txt")

    alignment_file = run_hunalign(src_file, tgt_file, dictionary)

    if alignment_file:
        aligned_data = parse_alignment(alignment_file, src_sentences, tgt_sentences)

        sentalign = { 
"version1": args.file1,
"version2": args.file2,
"method": "Hunalign on raw XML",
"script": "hunalign.py",
"sentences": aligned_data
}

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(sentalign, f, indent=4, ensure_ascii=False)

        print(f"Alignment saved to {output_json}")

    # Cleanup temp files
    os.remove(src_file)
    os.remove(tgt_file)
    if alignment_file:
        os.remove(alignment_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align TEI/XML sentences using Hunalign.")
    parser.add_argument('file1', type=str, help='Path to the first file (witness A)')
    parser.add_argument('file2', type=str, help='Path to the second file (witness B)')
    parser.add_argument('--output', type=str, help='Output filename')
    parser.add_argument("--dict", help="Optional bilingual dictionary file for Hunalign", default=None)

    args = parser.parse_args()
    outfile = args.output or "Alignments/output.json"
    main(args.file1, args.file2, outfile, args.dict)
