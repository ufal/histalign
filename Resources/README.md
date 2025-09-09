# Resources

This folder contains the gold standard alignment data for all pairs of texts in the experiment. 
All data are in JSON format, with metadata about the pair of texts that is aligned, and a list 
of aligned sentences by sentence ID. The name of each file is gold-XY.json, indicating it is
a gold standard alignment between files X and Y, where the identifiers of each text are explained
in the table below.

| ID | Lang | Description                               | #Texts | #Tokens |
|----|------|-------------------------------------------|--------|---------|
| A  | grc  | Edition by Sieber                         | 52     | 1762    |
| B  | chu  | Edition by Jouravel                       | 267    | 5068    |
| C  | deu  | Translation by Bonwetsch                  | 241    | 6584    |
| D  | deu  | Translation of B by Jouravel              | 270    | 6552    |
| E  | chu  | Transcription of manuscript used for B    | 702    | 4561    |

All JSON files are generated from the TEI/XML files of the project, where each item contains
the ID of the sentence node(s) in the source text, the full text in the source text of the 
sentence(s), and then the identifiers and text for the aligned text in the target text.