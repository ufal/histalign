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

The version C is taken from [Perseus](https://scaife.perseus.org/reader/urn:cts:greekLit:tlg2959.tlg004.opp-ger1:1.1-1.2/), and is a digital version of the following book:

> Bonwetsch, G. (Ed.). (1917). _De lepra._ In *Werke* (pp. 449–474). Berlin, Boston: De Gruyter.

The other versions are all taken from the digital version of the following book:

> Jouravel, A., & Sieber, J. (2024). The Greek and Slavonic Transmission of Methodius' De lepra. In K. Bracht, A. Jouravel, & J. Sieber (Eds.), Methodius of Olympus: De lepra: Interdisciplinary Approaches (pp. 11–30). De Gruyter.  


All data minus version C were gracefully made available for non-commercial use to the Berlin-Brandenburgische Akademie der Wissenschaften.
Please bear in mind that any commercial use of these sources is strictly prohibited.

All JSON files are generated from the TEI/XML files of the project, where each item contains
the ID of the sentence node(s) in the source text, the full text in the source text of the 
sentence(s), and then the identifiers and text for the aligned text in the target text.
