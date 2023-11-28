========================================
Conversion of BioC formatted annotations
========================================

Overview
--------

There are different ways to extract and convert the annotations in a BioC XML
file. For training and to calculate performance stats, we convereted the
annotations and the relevant sentences to IOB/BIO format. Additionally, we
provide commandline tools that allow the conversion of annotations and relevant
sentences to tab-separated CSV and JSON dictionary.

Conversion to IOB for training
------------------------------

In order to create annotations in IOB formatting ready for training a NER model
the annotated BioC XML files were converted with our corresponding commandline
tool. This iterates over all blocks of text in a passage/paragraph in the XML
file and extracts the relevant sentences and their respective annotations. The
input for the script is a pointer to a directory containing annotated BioC XML
files. The output of the tool will be four different files. A combined file
for all the documents in the input directory will be created as "all.tsv".
Additionally, there are three files for training prepared, "train.tsv" providing
a training set, "dev.tsv" providing a development set used during training and
"test.tsv" a final testing set.


**Example**

.. code-block:: bash

    ner_for_protein_structures.process_bioc_xml_for_training --bioc-xml-dir=test/data/annotated_BioC_XML/ --output-dir=test/results/IOB_for_training/


Conversion to IOB to calculate performance statistics
-----------------------------------------------------

In order to be able to calculate performance stats for an algorithm or for
a human annotator all annotations need to be provided as IOB formatted
annotations. The commandline tool below converts the annotations from BioC
format to IOB but only for the selected sections we were interested in, i.e.
title, abstract, introduction, results, discussion, tables as well as table
and figure captions for a given publication.

The tool can be run in two ways. By specifying an annotator name as string
through the parameter "annotator", one can extract annotations created by a
specific annotator. This is useful if analysing the performance of the
different annotators. If no annotator is specified, then the tool defaults
to "None" for this parameter, and therefore all annotations are used and a
single annotator for the document is assumed.

A combined file for all the documents in the input directory will be created as
"all.tsv".

**Example**

Specifying an annotator

.. code-block:: bash

    ner_for_protein_structures.process_bioc_xml_for_performance_stats --bioc-xml-dir=test/data/annotated_BioC_XML/ --output-dir=test/results/IOB_for_performance_stats_w_annotator/ --annotator="melaniev@ebi.ac.uk"


Not specifying an annotator

.. code-block:: bash

    ner_for_protein_structures.process_bioc_xml_for_performance_stats --bioc-xml-dir=test/data/annotated_BioC_XML/ --output-dir=test/results/IOB_for_performance_stats_wo_annotator/


Conversion of annotations and respective sentences to JSON
----------------------------------------------------------
This tool can be run on a directory containing a number of BioC
formatted XML files containing annotations. The annotations were
either produced by a human annotator in the annotation tool TeamTat
or they have been created by an automated named entity recognition tool
that predicts entity types and writes them into a BioC XML file.

The tool will create a key with the unique PubMedCentral ID from the
XML tags and add a list of sentence dictionaries to each publication
under the key "annotations". Each sentence dictionary has the following
keys: "sid" as unique sentence ID, "sent" a string of the respective sentence,
"section" gives the section of the publication the sentence and the annotations
were found in, "ner" contains a nested list of the annotations for for the
sentence. The sub-list for each annotation has the following elements:
"starting character position", "ending character position", "covered test span",
"entity type of the annotation".

The JSON file written to disk will be named "annotations.json"

**Example**

.. code-block:: bash

    ner_for_protein_structures.bioc_annotations_to_json --bioc-xml-dir=test/data/annotated_BioC_XML/ --output-dir=test/results/JSON_annotations_only/



Conversion of annotations and respective sentences to CSV
---------------------------------------------------------
This tool produces an alternative format for the annotations held in a BioC
formatted XML file. The annotations in the XML file can either be predictions
produced by one of our trained NER models or they may have been manually
created in an annotation process using the annotation tool TeamTat.

The tool will use the input XML and its BioC specific tags to find the 
relevant sentences in the text passages/paragraphs and the respective
annotations. Additionally, the tool will look fo the section tag to help
identify in which part of the publication the annotations have been found.
In turn, a tab separated CSV file is produced with the following column labels:
"anno_start", "anno_end", "anno_text", "entity_type", "sentence", "section".
For each XML file in the input directory a separate CSV file is produced
following the naming convetion: `<unique PubMedCentral ID>.csv`

The only input necessary, are a pointer to the directory on disk where
the BioC formatted, annotated XML files are found and an output directory
to write the produced CSV file to.

**Example**

.. code-block:: bash

    ner_for_protein_structures.bioc_annotations_to_csv --bioc-xml-dir=test/data/annotated_BioC_XML/ --output-dir=test/results/CSV_annotations_only/