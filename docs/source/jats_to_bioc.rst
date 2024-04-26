===========================================================
Conversion of EuropePMC or JATS style XML to BioC style XML
===========================================================

Overview
--------

In order to be able to make predictions, the publication text needs to be
provided in BioC format. If publication text is only available in JATS
XML, as for example after downloading an open access paper from EuropePMC,
then this publication can be formatted to BioC using the tool below.


Conversion to BioC XML
----------------------

The input for this tool is a directory holding JATS style XML files. Returned
are BioC style XML files in a specified output directory.


**Example**

.. code-block:: bash

    ner_for_protein_structures.pmcxml_to_biocxml --pmcxml-dir=test/data/JATS_xml/ --output-dir=test/results/JATS_to_BioC/
