======
Models
======

A number of models have been trained and can be chosen from. The models can
either be downloaded from Huggingface and run locally or can be contacted
through the Huggingface inference API and run remotely.

.. _models:

Available models
----------------

Currently, November 2023, there are five models available for this project.
Four are based on the pre-trained algorithm `PubmedBERT from 
Microsoft <https://huggingface.co/microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext>`_
and one is based on `Bioformer 8L <https://huggingface.co/bioformers/bioformer-8L>`_,
which is much smaller than the PubMed BERT model but with comparable performance.

The different models have been benchmarked with an independent set of 10
publications.

================ =============================================================================== ================ ============
model            Huggingface link                                                                no. entity types size on disk
================ =============================================================================== ================ ============
PubmedBERT v1.2  https://huggingface.co/PDBEurope/BiomedNLP-PubMedBERT-ProteinStructure-NER-v1.2               19     872.1 MB
PubmedBERT v1.4  https://huggingface.co/PDBEurope/BiomedNLP-PubMedBERT-ProteinStructure-NER-v1.4               19     872.1 MB
PubmedBERT v2.1  https://huggingface.co/PDBEurope/BiomedNLP-PubMedBERT-ProteinStructure-NER-v2.1               20     872.1 MB
PubmedBERT v3.1  https://huggingface.co/PDBEurope/BiomedNLP-PubMedBERT-ProteinStructure-NER-v3.1               20     872.1 MB
Bioformer8L v0.1 https://huggingface.co/PDBEurope/Bioformer8L-ProteinStructure-NER-v0.1                        20     356.4 MB
================ =============================================================================== ================ ============

**NOTE:** The statistics given below for each model are calculated for their respective
test set and any direct comparison between the versions should be done with caution.


Overall performance stats on respective test sets
-------------------------------------------------

Here the overall performance statistics for the different models on their
respective test sets.

================ ================= ============== ================== ================
model            overall precision overall recall overall F1 measure overall accuracy
================ ================= ============== ================== ================
PubmedBERT v1.2               0.87           0.89               0.88             0.95
PubmedBERT v1.4               0.90           0.92               0.91             0.96
PubmedBERT v2.1               0.90           0.92               0.91             0.96
PubmedBERT v3.1               0.91           0.92               0.91             0.96
Bioformer8L v0.1              0.88           0.92               0.90             0.95
================ ================= ============== ================== ================

All the models are close in their overall performance but diverge when looking
at the different entity types.


Per-entity type precision on respective test sets
-------------------------------------------------

=================== =============== =============== =============== =============== ================
entity type         PubmedBERT v1.2 PubmedBERT v1.4 PubmedBERT v2.1 PubmedBERT v3.1 Bioformer8L v0.1
=================== =============== =============== =============== =============== ================
bond_interaction                  -               -            0.93            0.82             0.93
chemical                       0.84            0.90            0.89            0.92             0.87
complex_assembly               0.85            0.88            0.91            0.89             0.88
evidence                       0.74            0.86            0.84            0.89             0.81
experimental_method            0.77            0.73            0.85            0.80             0.81
gene                           0.86            0.89            0.79            0.79             0.71
mutant                         0.83            0.93            0.91            0.92             0.92
oligomeric_state               0.94            0.88            0.93            0.96             0.93
protein                        0.91            0.97            0.94            0.96             0.94
protein_state                  0.80            0.78            0.83            0.86             0.80
protein_type                   0.85            0.84            0.85            0.85             0.82
ptm                            0.88            0.64            0.70            0.85             0.71
residue_name                   0.86            0.97            0.92            0.74             0.87
residue_name_number            0.99            0.98            0.95            0.96             0.93
residue_number                 1.00            1.00            0.80            0.70             0.77
residue_range                  1.00            0.86            0.81            0.89             0.79
site                           0.83            0.83            0.85            0.88             0.86
species                        0.96            0.97            0.94            0.95             0.97
structure_element              0.88            0.91            0.91            0.91             0.90
taxonomiy_domain               0.95            0.97            0.99            0.98             0.98
=================== =============== =============== =============== =============== ================

Per-entity type recall on respective test sets
----------------------------------------------

=================== =============== =============== =============== =============== ================
entity type         PubmedBERT v1.2 PubmedBERT v1.4 PubmedBERT v2.1 PubmedBERT v3.1 Bioformer8L v0.1
=================== =============== =============== =============== =============== ================
bond_interaction                  -               -            0.88            0.91             0.83
chemical                       0.90            0.93            0.91            0.91             0.91
complex_assembly               0.76            0.91            0.93            0.90             0.91
evidence                       0.76            0.89            0.88            0.88             0.90
experimental_method            0.75            0.76            0.85            0.82             0.82
gene                           0.92            0.86            0.86            0.65             0.87
mutant                         0.92            0.95            0.97            0.94             0.95
oligomeric_state               1.00            1.00            0.99            1.00             0.99
protein                        0.93            0.97            0.97            0.96             0.97
protein_state                  0.83            0.85            0.88            0.88             0.86
protein_type                   0.84            0.90            0.85            0.88             0.86
ptm                            0.76            0.81            0.70            0.79             0.69
residue_name                   0.95            0.92            0.97            0.96             0.92
residue_name_number            0.99            0.99            0.96            0.98             0.99
residue_number                 1.00            0.93            0.97            0.73             0.91
residue_range                  0.80            0.91            0.70            0.86             0.75
site                           0.82            0.86            0.87            0.90             0.88
species                        0.98            1.00            0.96            0.95             0.96
structure_element              0.86            0.92            0.92            0.92             0.92
taxonomiy_domain               0.97            0.96            0.98            0.98             0.95    
=================== =============== =============== =============== =============== ================

Per-entity type F1 measure on respective test sets
--------------------------------------------------

=================== =============== =============== =============== =============== ================
entity type         PubmedBERT v1.2 PubmedBERT v1.4 PubmedBERT v2.1 PubmedBERT v3.1 Bioformer8L v0.1
=================== =============== =============== =============== =============== ================
bond_interaction                  -               -            0.90            0.86             0.88
chemical                       0.87            0.92            0.90            0.92             0.89
complex_assembly               0.80            0.89            0.92            0.90             0.90
evidence                       0.75            0.88            0.86            0.89             0.85
experimental_method            0.76            0.75            0.85            0.81             0.81
gene                           0.89            0.88            0.82            0.71             0.78
mutant                         0.88            0.94            0.94            0.93             0.93
oligomeric_state               0.97            0.93            0.96            0.98             0.96
protein                        0.92            0.97            0.95            0.96             0.96
protein_state                  0.81            0.81            0.85            0.87             0.82
protein_type                   0.84            0.87            0.85            0.87             0.84
ptm                            0.81            0.71            0.70            0.82             0.70
residue_name                   0.91            0.94            0.94            0.84             0.89
residue_name_number            0.99            0.99            0.96            0.97             0.96
residue_number                 1.00            0.96            0.88            0.71             0.83
residue_range                  0.89            0.89            0.75            0.87             0.77
site                           0.82            0.85            0.86            0.89             0.87
species                        0.97            0.98            0.95            0.95             0.96
structure_element              0.87            0.91            0.92            0.91             0.91
taxonomiy_domain               0.96            0.97            0.98            0.98             0.96
=================== =============== =============== =============== =============== ================