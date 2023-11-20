=========================================================
Calculating performance stats following SemEval procedure
=========================================================

Overview
--------

To be able to judge the performance of the trained model, we used the SemEval
evaluation procedure as published here `SemEval <https://aclanthology.org/S13-2056.pdf>`_.
Each predicted annotation was assessed whether it had a matching annotation in
the ground truth and whether this match was *"correct"*, *"incorrect"*, *"partial"*,
*"missing"* or *"spurious"*. We then evaluated a found match whether it
belonged to one of four different classes of matches: *"strict"*, *"exact"*,
*"partial"* or *"type"*. *"Strict"* evaluation expected a perfect match between
span boundaries and the annotated entity type. For an *"exact"* match
the span boundaries are expected to be identical but the entity type for the
span was ignored. If only part of the text spans matched, then an annotation
was evaluated as *"partial"* and the entity type was ignored. A *"type"* match
required some overlap between the predicted and the ground truth annotation.
For each class of match the precision, recall and F1 measure were determined.
The statistics were calculated for the selected sections title, abstract,
introduction, results, discussion, tables as well as table and figure captions.

In order to calculate the performance statistics, the input data is assumed to
be annotations in IOB format. A comparison is made between two files, one
of which is repesenting the ground truth and the other being annotations from
either an algorithm as predictions or manually created by a human annotator.

Additionally, a text file containing the entity type labels that are present
in the IOB format must be provided.

Optionally, the label integrity can be checked by leaving the default of
"--validate-labels". This ensures that the IOB labels have been kept in correct
order, i.e. that there is no "O" (for outside) in the middle of an annotation,
if the annotation contains multiple word tokens.

The tool will calculate the performance statistics and write them to a text
file in the defined output directory. The text file follows the naming
convention `<current date>_SemEval_report.txt`. If no output directory has
been specified, the file will be written to the current directory.

**Example**

.. code-block:: bash

    ner_for_protein_structures.run_semeval_analysis --ground-truth-IOB=test/data/SemEval/PMC4772114_ground_truth_all_IOB.tsv --annotated-IOB=test/data/SemEval/PMC4772114_autoannotator_v1.2_all_IOB.tsv --validate-labels="True" --entity-types=test/data/SemEval/entity_types.txt  --output-dir=test/results/SemEval_analysis/

