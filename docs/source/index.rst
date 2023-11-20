.. ner_for_protein_structures documentation master file, created by
   sphinx-quickstart on Wed Nov  1 14:21:53 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ner_for_protein_structures's documentation!
======================================================

**ner_for_protein_structures** represents a collection of commandline tools
published alongside a scientific publication describing the
development of a human-in-the-loop named entity recognition algorithm specific
for protein structures.

The tools described here allow  for the convertion of annotations in BioC 
formatted XML files into a number of other formats for the calculation of
performance statistics and to prepare intput data for model training. An
inference script is also provided, which allows the submission of other BioC
formatted XML files for inference via the Huggingface inference API.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   preparation
   conversions
   predictions
   semeval_stats
   functions


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
