===============
Getting Started
===============


**ner_for_protein_structures** package is published alongside a scientific publication describing the
development of a human-in-the-loop named entity recognition algorithm specific
for protein structures.

Here we provide a number of command line tools to convert annotations found in
BioC formatted XML files, as they have been exported from our annotation tool
TeamTat (https://www.teamtat.org/), into other formats.

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


Get all the commandline tools into the path

.. code-block:: bash

    pip install .

