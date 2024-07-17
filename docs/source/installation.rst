===============
Getting Started
===============


**ner_for_protein_structures** package is published alongside a scientific publication
describing the development of a human-in-the-loop named entity recognition algorithm
specific for protein structures.

Here we provide a number of command line tools to convert annotations found in
BioC formatted XML files, as they have been exported from our annotation tool
TeamTat (https://www.teamtat.org/), into other formats. The BioC format is the
core data format for the publications as XML text. It was developed by the
BioCreative Initiative and is documented here (https://bioc.sourceforge.net/).
We also provide a tool to calculate performance statistics following the
SemEval procedure (`SemEval <https://aclanthology.org/S13-2056.pdf>`_).

Installation
------------

Clone the repository from the `source code <git@github.com:PDBeurope/ner_for_protein_structures.git>`_ on Github:

.. code-block:: bash

    git clone git@github.com:PDBeurope/ner_for_protein_structures.git



It is good practice to create a `virtual environment <https://realpython.com/python-virtual-environments-a-primer/>`_ for development:

.. code-block:: bash

    python3 -m venv ner_venv


Now activate the venv.

.. code-block:: bash

    source ner_venv/bin/activate


Next, install all the necessary dependencies using the provided requirements.txt

.. code-block:: bash

    pip install -r requirements.txt


To be able to use some of the NLP tools install the scientific, English language
model from `Scispacy <https://allenai.github.io/scispacy/>`_

.. code-block:: bash

    pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz



Downloading and setting up models
---------------------------------

The different available models, their performance stats and download links are
given in section :ref:`models`. Huggingface supports git and all models can
simply be downloaded through "git clone". However, as the binary file for the
models is too large for standard git, the large-file handler needs to be
installed in the parent directory the model will be cloned into.

.. code-block:: bash

    git lfs install

After the large-file handler was installed, the models can be cloned from
Huggingface as in the example below.

.. code-block:: bash

    git clone https://huggingface.co/PDBEurope/Bioformer8L-ProteinStructure-NER-v0.1

Alternatively, the models can be accessed through Huggingface's inference API.
This option does require a Huggingface account and an authentication token. The
details on how to register and how to set up the token can be found on `Huggingface <https://huggingface.co/>`_



Annotation handbook and TeamTat user guide
------------------------------------------

The annotation handbook with details on how to annotate different entity types
and the user guide on the annotation tool TeamTat have been made available and
can be found here:

:download:`Annotation handbook and user guide <../user_guide_and_annotation_handbook_to_Sci_Data_v2.pdf>`.

