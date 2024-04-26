================
Data Preparation
================

.. _get-publications:
Prepare some data
-----------------

The scripts are based on BioC formatted XML versions of scientific publications.
Details about the BioC format can be found here:

It is also assumed that the annotations have been created by either manual
annotation using TeamTat (https://www.teamtat.org/) and downloaded as BioC XML
or they have been predicted using one of the four models that have been
developed and are described in the associated publication.


Downloading BioC XML files from an open access collection
---------------------------------------------------------

For any scientific publication that may contain structural information and that
is open access, one can download a BioC formatted XML version through an FTP
service provided by the National Center for Biotechnology Information (NCBI).
The site can be found here: 
https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

All the documents available via this service are identified by their unique
PubMedCentral IDs.

We provide a small commandline tool that will fetch any open access publications
in BioC XML from this FTP site given a list of PubMedCentral IDs. PubMedCentral
IDs are constructed of a 3-letter source identifier "PMC" and a multi-digit
numerical part, e.g. "PMC4784909". The example here refers to the publication 
`The Structural Basis of Coenzyme A Recycling in a Bacterial Organelle <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4784909/>`_.
The downloaded files will be named `"<date>_xml_<unique PMC ID>.xml"`


**Example**

.. code-block:: bash

    ner_for_protein_structures.get_bioc_xml_from_pmc --pmcid-list=test/data/pmcid_list_for_ftp_retrieval.txt --output-dir=test/results/BioC_XML_from_FTP/


Conversion of EuropePMC or JATS style XML to BioC style XML
-----------------------------------------------------------

In order to be able to make predictions, the publication text needs to be
provided in BioC format. If publication text is only available in JATS
XML, as for example after downloading an open access paper from EuropePMC,
then this publication can be formatted to BioC using the tool below. The
input for this tool is a directory holding JATS style XML files. Returned
are BioC style XML files in a specified output directory.

**Example**

.. code-block:: bash

    ner_for_protein_structures.pmcxml_to_biocxml --pmcxml-dir=test/data/JATS_xml/ --output-dir=test/results/JATS_to_BioC/

