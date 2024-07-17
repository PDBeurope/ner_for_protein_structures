===============================================
Make predictions on un-annotated BioC XML files 
===============================================


For usage of the models in the context of this project two commandline tools
have been provided. One tool contacts the Huggingface inference API to
make predictions the other relies on the model having been downloaded locally.
In both cases the input text needs to be provided as BioC formatted XML files.
The publications can either have been downloaded from an open access collection
already pre-formatted in BioC as described in :ref:`get-publications` or may
have  been created from a local PDF by other means.


Accessing the models through Huggingface inference API
------------------------------------------------------

To access the models through the inference API one needs to have the input text
formatted as BioC XML as well as an account with Huggingface and an access token.
If one followed the instructions for creating a virtual environment for the 
project and activated it, all the necessary dependencies should have been
installed. The name of the remote model on Huggingface needs to be given. 

**Example**

.. code-block:: bash

    ner_for_protein_structures.run_hf_inference_for_ner --xml-dir=test/data/not_annotated_BioC_XML/ --model-repo="PDBEurope/Bioformer8L-ProteinStructure-NER-v0.1" --auth-token="<my_hf_access_token>" --output-dir=test/results/predictions/

Although a waiting step has been added in the inference script, the API does have
a lag phase which may cause some text passages not having any annotations. Also,
anyone running requests on a free plan will find that the API has an access limit
per hour which can easily be reached by just running two publications of average
length.


Accessing the models locally
----------------------------

The models can also be accessed loacally after download. They use between 350MB and
900MB of disk space. The input publications need to be formatted in BioC and
provided as XML. Model location needs to be provided as full path. A short-hand
for the model name should be provided as this will be added as "annotator" in the
annotations to determine the origin of the annotation.

The smaller bioformer8L and the larger PubmedBERT models both have been tested
locally on a MacBook Pro M1 with 16GB RAM running Sonoma 14.1.1.


**Example**

.. code-block:: bash

    ner_for_protein_structures.run_local_inference_for_ner --xml-dir=test/data/not_annotated_BioC_XML/ --model-dir=<full_path_to_model_location> --model-name="bioformer8L_v0.1" --output-dir=test/results/predictions/

.. code-block:: bash
    
    ner_for_protein_structures.run_local_inference_for_ner --xml-dir=test/data/not_annotated_BioC_XML/ --model-dir=<full_path_to_model_location> --model-name="pubmedbert_v2.1" --output-dir=test/results/predictions/
