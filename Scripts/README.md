# Scripts

This folder contains the relevant scripts to create an automatic alignment between two version of a text, 
where both texts are in the TEITOK TEI/XML format, are tokenized and segmented into sentences. The alignment
is created as a JSON file, that can then be correted, and imported back into the TEI/XML source. There are 
alignment script for three alignment algorithms, the script to load the JSON, and a script to calculate the 
Alignment Error Rate (AER) between two JSON alignment files for the same text.

All scripts are intended to be used together with TEITOK, which provides an easy graphical interface to 
correct the automatic alignment before loading the alignment into the XML files. 

## hunalign.py

The script `hunalign.py` is a python wrapper for the hunalign command-line interface (which is hence expected 
to be installed), and reads two segmented TEITOK/XML files and creates a JSON file with sentence level 
alignments.

```python hunalign.py [options] (source XML) (target XML)```

The options are `--output` to specify a name for the output JSON file, and `--dict` to optionally provide a bilingual
dictionary in the format expected by hunalign.


## labse.py

The script `labse.py` is a python script that uses sentences aligners with the LaBSE model to provide an automatic 
alignment between two texts. 
It reads two segmented TEITOK/XML files and creates a JSON file with sentence level alignments. 

```python labse.py [options] (source XML) (target XML)```

The options are `--output` to specify a name for the output JSON file. The model used 
can easily be changed in the script, but is not currently a command line option.

## awesome.py


## loadalign.pl

The script `loadalign.pl` is a Perl script to load a JSON alignment file into a TEITOK/XML representation. The JSON 
file contains the information which two TEI/XML files are being linked, and will assume the first (source) of the two files
to contain `@tuid` attributes for all elements to be aligned. It will then use the alignment to assign appropriate `@tuid` attributes to the target file.

## computer-aer.py

The script `compute-aer.py` is a Python script that calculates the error rate (AER) in a JSON alignment file when
compared to a gold standard. The output is a simple value. Usage:

```python computer-aer.py [gold-standard JSON] [computed JSON]```
