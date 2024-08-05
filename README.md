# ner_for_protein_structures

This package is published alongside a scientific publication describing the
development of a human-in-the-loop named entity recognition algorithm specific
for protein structures.

Here we provide a number of command line tools to convert annotations found in
BioC formatted XML files, as they have been exported from our annotation tool
TeamTat (https://www.teamtat.org/), into other formats.

For more details read the documentation here: https://ner-for-protein-structures.readthedocs.io/en/latest/

## Installation
Clone the repository from the [source code](https://github.com/PDBeurope/ner_for_protein_structures.git) on Github:

```bash
git clone https://github.com/PDBeurope/ner_for_protein_structures.git
```

It is good practice to create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for development:

```bash
python3 -m venv ner_venv
```

Now activate the venv.

```bash
source ner_venv/bin/activate
```

Next, install all the necessary dependencies using the provided requirements.txt
```bash
pip install -r requirements.txt
```

To be able to use some of the NLP tools install the scientific, English language model
```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz
```

## Downloading models

The different available models, their performance stats and download links are
given in section "Models" of the documentation. Huggingface supports git and all
models can simply be downloaded through "git clone", see example below. However,
as the binary file for the models is too large for standard git, the large-file
handler needs to be installed in the parent directory the model will be cloned
into.

```bash

git lfs install

```

After the large-file handler was installed, the models can be cloned from
Huggingface as in the example below.

```bash

git clone https://huggingface.co/PDBEurope/Bioformer8L-ProteinStructure-NER-v0.1
```

Alternatively, the models can be accessed through Huggingface's inference API.
This option does require a Huggingface account and an authentication token. The
details on how to register and how to set up the token can be found on [Huggingface](https://huggingface.co/)

## Annotation handbook and TeamTat user guide

The annotation handbook with details on how to annotate different entity types
and the user guide on the annotation tool TeamTat can be found here: [Annotation handbook and user guide](docs/user_guide_and_annotation_handbook_to_Sci_Data_v2.1.pdf)


## Support
For any feedback, help, bug report please email to:
melaniev@ebi.ac.uk


## Authors

This repository was developed at **European Bioinformatics Institute**

- Lead Developer: Melanie Vollmar


## License
This project is covered by an MIT license.

