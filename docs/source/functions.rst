========================================
List of functions in the tool collection
========================================

Overview
--------

Below is a collection of the various functions included in this package.
Detailed descriptions can be found in their respective sections.

Convert annotations in BioC formatted XML to CSV
------------------------------------------------

.. autofunction:: ner_for_protein_structures.annotation_conversion.bioc_annotations_to_csv.main


Convert annotations in BioC formatted XML to JSON
-------------------------------------------------

.. autofunction:: ner_for_protein_structures.annotation_conversion.bioc_annotations_to_json.main


Fetch fulltext, open access publications in BioC formatted XML using PubMedCentral IDs
--------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.bioc_xml_retrieval.get_bioc_xml_from_pmc.main


Run NER predictions on BioC formatted XML files with a trained model - locally
------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.ner_inference.run_local_inference_for_ner.main


Run NER predictions on BioC formatted XML files with a trained model - remotely
-------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.ner_inference.run_hf_inference_for_ner.main


Processing BioC formatted XML files to turn annotations into IOB format for SemEval calculations
-------------------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.annotation_conversion.process_bioc_xml_for_performance_stats.main


Processing BioC formatted XML files to turn annotations into IOB format for model training
------------------------------------------------------------------------------------------

.. autofunction:: ner_for_protein_structures.annotation_conversion.process_bioc_xml_for_training.main


Running SemEval to calculate performance statistics
---------------------------------------------------

.. autofunction:: ner_for_protein_structures.sem_eval.run_semeval_analysis.main


Converting EuropePMC/JATS style XML to BioC XML
-----------------------------------------------

.. autofunction:: ner_for_protein_structures.bioc_xml_tools.pmcxml_to_biocxml:main