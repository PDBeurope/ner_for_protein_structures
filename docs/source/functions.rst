========================================
List of functions in the tool collection
========================================

Overview
--------

Below is a collection of the various functions included in this package.
Detailed descriptions can be found in their respective sections.

Convert annotations in BioC formatted XML to CSV
------------------------------------------------

.. autofunction:: ner_for_protein_structures.bioc_annotations_to_csv


Convert annotations in BioC formatted XML to JSON
-------------------------------------------------

.. autofunction:: ner_for_protein_structures.bioc_annotations_to_json


Fetch fulltext, open access publications in BioC formatted XML using PubMedCentral IDs
--------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.get_bioc_xml_from_pmc


Run NER predictions on BioC formatted XML files with a trained model
--------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.make_ner_predictions


Processing BioC formatted XML files to turn annotations into IOB format for SemEval calculations
-------------------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.process_bioc_xml_for_performance_stats


Processing BioC formatted XML files to turn annotations into IOB format for model training
------------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.process_bioc_xml_for_training


Running SemEval to calculate performance statistics
---------------------------------------------------

.. autofunction:: ner_for_protein_structures.run_semeval_analysis