# ner_for_protein_structures

This package is published alongside a scientific publication describing the
development of a human-in-the-loop named entity recognition algorithm specific
for protein structures.

Here we provide a number of command line tools to convert annotations found in
BioC formatted XML files, as they have been exported from our annotation tool
TeamTat (https://www.teamtat.org/), into other formats.

## Instalation
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

To be able to use some of the NLP tools install the scientific, english language model
```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz
```

Get all the commandline tools into the path
```bash
pip install .
```

## Support
For any feedback, help, bug report please email to:
melaniev@ebi.ac.uk


## Authors

This repository was developed at **European Bioinformatics Institute**

- Lead Developer: Melanie Vollmar


## License
This project is covered by an MIT license.
