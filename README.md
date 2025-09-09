# Alignment of Historical Manuscript Transcriptions and Translations

This repository presents a collection of scripts and resources to align transcriptions and translations of historical documents. These scripts and resources accompany the following article:

> Janssen, M., Lendvai, P., & Jouravel, A. (2025).  
> *Alignment of Historical Manuscript Transcriptions and Translations*.  
> In *Proceedings of the International Conference on Recent Advances in Natural Language Processing (RANLP)*, Varna, Bulgaria.

The scripts are arranged around two formats: the TEI/XML format used in [TEITOK](http://www.teitok.org/), which aligns nodes in multiple XML documents via a shared ID, and a JSON format for pairwise alignment between two documents. There are scripts to create a JSON file that aligns two TEI/XML documents using three different alignment algorithms: [Hunalign](http://mokk.bme.hu/en/resources/hunalign/), [Awesome-Align](https://huggingface.co/aneuraz/awesome-align-with-co), and [LabBSE](https://huggingface.co/sentence-transformers/LaBSE). There are scripts to incorporate a JSON file into a TEI/XML file to generate a TEITOK-style alignment. And there are scripts to generate a TMX file from either two TEI/XML documents or a JSON file to be able to use the alignment in other applications. 

The sources contain the manually verified aligned data, organized as JSON file over pairs of documents.

The BibTeX citation for the article mentioned above:

```bibtex
@inproceedings{janssenetal2025,
  author  = {Maarten Janssen and Piroska Lendvai and Anna Jouravel},
  title   = {Alignment of Historical Manuscript Transcriptions and Translations},
  booktitle = {Proceedings of the International Conference on Recent Advances in Natural Language Processing (RANLP)},
  year      = {2025},
  address   = {Varna, Bulgaria},
}
```

