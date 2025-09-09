# Create a bilingual sentence alignment as a JSON using LaBSE
# Language-Agnostic BERT Sentence Embedding

import sys
import argparse
import lxml.etree as ET
from datetime import datetime
import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from polyfuzz import PolyFuzz
from polyfuzz.models  import Embeddings
from flair.embeddings import TransformerWordEmbeddings
from flair.embeddings import SentenceTransformerDocumentEmbeddings

startTime = datetime.now()
# model initialization
embeddings = SentenceTransformerDocumentEmbeddings('LaBSE')
LaBSE = Embeddings(embeddings, min_similarity=0, model_id="LaBSE")
model = PolyFuzz([LaBSE])

# TF-IDF (not good prob.)
# LaBSE 								 : trained on 100+ languages
# distiluse-base-multilingual-cased-v2   : balance between speed and ML
# paraphrase-multilingual-MiniLM-L12-v2  : lightweight and fast
# xlm-r-distilroberta-base-paraphrase-v1 : robust for LRL

msg = "Run PolyFuzz on two TEITOK/XML files to produce a sentence alignment"

# Initialize parser & add arguments
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("-i1", "--input1", help = "Input TEITOK file1")
parser.add_argument("-i2", "--input2", help = "Input TEITOK file2")
parser.add_argument("-o", "--output", help = "Output CSV file", default="tmp/labse.json")
parser.add_argument("-e", "--encoding", help = "TXT encoding type (utf8 or utf-16)", default="utf8")
args = parser.parse_args()

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


source = extract_sentences(args.input1)
target = extract_sentences(args.input2)

source_ids, source_texts = zip(*source)
target_ids, target_texts = zip(*target)

#perform matching
model.match(source_texts, target_texts)
matches = model.get_matches()

source_id_map = dict(source)
target_id_map = dict(target)


aligned_data = []

for i, row in matches.iterrows():
    from_text = row["From"]
    to_text = row["To"]
    similarity = row["Similarity"]

    from_id = source_ids[i]
    to_id = target_ids[target_texts.index(to_text)] if to_text in target_texts else None

    rec = { "id1": from_id, "text1": from_text, "id2": to_id, "text2": to_text, "similarity": similarity }

    aligned_data.append(rec)

sentalign = { 
"version1": args.input1,
"version2": args.input2,
"method": "SentenceTransformer on raw XML",
"script": "labse.py",
"model": "LaBSE",
"sentences": aligned_data
}

with open(args.output, "w", encoding="utf-8") as f:
	json.dump(sentalign, f, indent=4, ensure_ascii=False)

