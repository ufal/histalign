from transformers import AutoModel, AutoTokenizer
import itertools
import torch
import argparse
import json
import lxml.etree as ET

# load model
model = AutoModel.from_pretrained("aneuraz/awesome-align-with-co")
tokenizer = AutoTokenizer.from_pretrained("aneuraz/awesome-align-with-co")

# model parameters
align_layer = 8
threshold = 1e-3

def extract_blobs(tei_file):
   # Extracts sentences and their IDs from a TEI XML file.
    tree = ET.parse(tei_file)
    root = tree.getroot()

    # Remove all <note> fields
    for note in root.findall('.//note'):
        parent = note.getparent()
        if parent is not None:
            parent.remove(note)   
            
    blobs = {}
    stxt[tei_file] = {}
    
    xp = '//' + args.blob
    if args.blob != 'text': xp = '//text//' + args.blob
    for blob in root.xpath( xp ):
        blob_id = blob.get(args.tuid, f"sent_{len(blobs) + 1}")  # Default ID if missing
        toklist = []
        for tok in blob.xpath('.//tok' ):
            tok_id = tok.get("id", blob_id + f"-_{len(toklist) + 1}")  # Default ID if missing
            tok_text = "".join(tok.itertext()).strip().replace("\n", " ")
            token = ( tok_id, tok_text )
            toklist.append(token)
        blobs[blob_id] = toklist

    # Map tokens onto their sentences
    if args.align != "tok":
        tok2s[tei_file] = {}
        for s in root.xpath('//text//' + args.align ):
            sent_id = s.get('id', 'xxxx')  # Default ID if missing
            text = "".join(s.itertext()).strip().replace("\n", " ")
            stxt[tei_file][sent_id] = text
            for tok in s.xpath('.//tok' ):
                tok_id = tok.get("id", 'xxxx')  # Default ID if missing
                tok2s[tei_file][tok_id] = sent_id
    
    return blobs

def create_align(align_words, src_sentence, tgt_sentence):
    for pair in align_words:
        srcid = pair[0]
        srctokid = src_sentence[srcid][0]
        srctok = src_sentence[srcid][1]
        tgtid = pair[1]
        tgttokid = tgt_sentence[tgtid][0]
        tgttok = tgt_sentence[tgtid][1]
        elem = { "id1": srctokid, "text1": srctok, "id2": tgttokid, "text2": tgttok}
        aligned_data.append(elem)

def print_align():
    for elem in aligned_data:
        print( elem['id1'] + ' = ' + elem['text1'] + ' => ' + elem['id2'] + ' = ' + elem['text2'] )

def write_json():

    output_json = outfile

    sentalign = { 
"version1": args.file1,
"version2": args.file2,
"method": "Awesome-align on raw XML",
"script": "awesome.py",
"blob": args.blob,
"alignment": args.align    ,
"tokens": aligned_data
}

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(sentalign, f, indent=4, ensure_ascii=False)


def sent_json():

    output_json = outfile
    aligned_sents = []

    # Map each sentenceID to 
    sentmap = {}
    for elem in aligned_data:
        id1 = elem['id1']
        id2 = elem['id2']
        if id1 in tok2s[args.file1]:
            sent1 = tok2s[args.file1][id1]
            if not sent1 in sentmap: sentmap[sent1] = {}
            if id2 in tok2s[args.file2]:
                sent2 = tok2s[args.file2][id2]
                if not sent2 in sentmap[sent1]: sentmap[sent1][sent2] = 0
                sentmap[sent1][sent2] = sentmap[sent1][sent2] + 1
    
    aligned_sents = []
    for sent1 in sentmap:
        tsids = []
        tstxts = []
        for sent2 in sentmap[sent1]:
            tsids.append(sent2)
            tstxts.append(stxt[args.file2][sent2])
        tsid = ','.join(tsids)
        tstxt = ' '.join(tstxts)
        elem = { "id1": sent1, "text1": stxt[args.file1][sent1], "id2": tsid, "text2": tstxt}
        aligned_sents.append(elem)
        
    sentalign = { 
"version1": args.file1,
"version2": args.file2,
"method": "Awesome-align on raw XML",
"script": "awesome.py",
"blob": args.blob,
"alignment": args.align    ,
"sentences": aligned_sents
}

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(sentalign, f, indent=4, ensure_ascii=False)

def align(sent_src, sent_tgt):
    # pre-processing
    # sent_src, sent_tgt = src.strip().split(), tgt.strip().split()
    token_src, token_tgt = [tokenizer.tokenize(word) for word in sent_src], [tokenizer.tokenize(word) for word in sent_tgt]
    wid_src, wid_tgt = [tokenizer.convert_tokens_to_ids(x) for x in token_src], [tokenizer.convert_tokens_to_ids(x) for x in token_tgt]
    ids_src, ids_tgt = tokenizer.prepare_for_model(list(itertools.chain(*wid_src)), return_tensors='pt', model_max_length=tokenizer.model_max_length, truncation=True)['input_ids'], tokenizer.prepare_for_model(list(itertools.chain(*wid_tgt)), return_tensors='pt', truncation=True, model_max_length=tokenizer.model_max_length)['input_ids']
    sub2word_map_src = []
    for i, word_list in enumerate(token_src):
      sub2word_map_src += [i for x in word_list]
    sub2word_map_tgt = []
    for i, word_list in enumerate(token_tgt):
      sub2word_map_tgt += [i for x in word_list]

    # alignment
    align_layer = 8
    threshold = 1e-3
    model.eval()
    with torch.no_grad():
      out_src = model(ids_src.unsqueeze(0), output_hidden_states=True)[2][align_layer][0, 1:-1]
      out_tgt = model(ids_tgt.unsqueeze(0), output_hidden_states=True)[2][align_layer][0, 1:-1]
    
      dot_prod = torch.matmul(out_src, out_tgt.transpose(-1, -2))
    
      softmax_srctgt = torch.nn.Softmax(dim=-1)(dot_prod)
      softmax_tgtsrc = torch.nn.Softmax(dim=-2)(dot_prod)
    
      softmax_inter = (softmax_srctgt > threshold)*(softmax_tgtsrc > threshold)
    
    align_subwords = torch.nonzero(softmax_inter, as_tuple=False)
    align_words = set()
    for i, j in align_subwords:
      align_words.add( (sub2word_map_src[i], sub2word_map_tgt[j]) )

    return(align_words)

# Command line arguments            
parser = argparse.ArgumentParser(description="Align TEI/XML sentences using Hunalign.")
parser.add_argument('file1', type=str, help='Path to the first file (witness A)')
parser.add_argument('file2', type=str, help='Path to the second file (witness B)')
parser.add_argument('--blob', type=str, help='Blob alignment level', default='s')
parser.add_argument('--align', type=str, help='Output alignment level', default='tok')
parser.add_argument('--tuid', type=str, help='Blob alignment attribute', default='tuid')
parser.add_argument('--output', type=str, help='Output filename')
parser.add_argument('--debug', action='store_true', help='Debug mode')

args = parser.parse_args()
outfile = args.output or "Alignments/output.json"

# Main function to extract texts, 
tok2s = {}
stxt = {}
src_sentences = extract_blobs(args.file1)
tgt_sentences = extract_blobs(args.file2)
if args.debug: print(src_sentences)

aligned_data = []
for align_id, src_sentence in src_sentences.items():
    if align_id in tgt_sentences:
        if args.debug: print(src_sentence)
        tgt_sentence = tgt_sentences[align_id]
        sent_src = [word for _, word in src_sentence]
        sent_tgt = [word for _, word in tgt_sentence]
        align_words = align(sent_src, sent_tgt)
        create_align(align_words, src_sentence, tgt_sentence)
    else:
        print("No such sentence in target: ", align_id)

if args.debug: print(aligned_data)

if args.align == "s":
    sent_json()
else:
    write_json()
