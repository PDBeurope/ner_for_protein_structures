#  importing necessary modules/libraries
import os
import argparse
import logging
import pandas as pd
import xml.etree.ElementTree as ET
from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification
from transformers import PreTrainedTokenizerFast
from transformers import pipeline
from datetime import datetime

def run_local_inference_for_ner(xml_dir, model_dir, model_name, output_dir):
    """
    make predictions using a local model on publications provided as
    BioC formatted XML; model location needs to be specified;
    returns BioC XML of the publication with annotations and
    saves them to disk in specified output directory
    """
    try:
        # check whether the input directory exists
        assert os.path.exists(xml_dir)
        content = os.listdir(xml_dir)
    except:
        logging.error(f"No input directory found")
        pass

    try:
        # check whether the model directory exists
        assert os.path.exists(model_dir)
        model = AutoModelForTokenClassification.from_pretrained(model_dir)
        logging.info(f"Instantiated the model")
    except:
        logging.error(f"No model directory found")
        pass

    try:
        # define the tokenizer and instanciate it for the fine-tuned model
        tokenizer = AutoTokenizer.from_pretrained(model_dir,
                                          model_max_length = 512,
                                          batch_size = 4,
                                          truncation = True)
        assert isinstance(tokenizer, PreTrainedTokenizerFast)
        logging.info(f"Instantiated the tokenizer")
    except:
        logging.error(f"Could not load tokenizer")

    date = datetime.strftime(datetime.now(), "%Y%m%d")

    # iterate over the BioC formatted XML files in the input directory
    for file in content:
        if file.endswith(".xml"):
            logging.info(f"Working on input file {file}")
            input = os.path.join(xml_dir, file)

            # using ElementTree to create an editable version of the input XML file
            tree = ET.parse(input)
            root = tree.getroot()

            # create a list of offsets for the passages in the XML file
            offset_list = [int(passage.find("offset").text) for passage in root.iter("passage")]

            para_length_list = []
            for passage in root.iter("passage"):
                try:
                    if passage.find("text").text is not None:
                        para_length = len(passage.find("text").text)
                        para_length_list.append(para_length)
                    else:
                        logging.error(f"Could not get paragraph length")
                except:
                    continue

            # creating a dataframe to keep track of offsets and textspan length
            # needed so the annotations can be written back in the XML with
            # correct location
            df_offset_start = pd.DataFrame (offset_list, columns = ['offset_start'])
            df_paragraph_length = pd.DataFrame (para_length_list, columns = ['paragraph_length'])
            df_start_end = pd.concat([df_offset_start, df_paragraph_length], axis = 1, ignore_index=True)
            df_start_end = df_start_end.fillna(0).astype(int)
            df_start_end.columns = ['offset_start', 'paragraph_length']
            df_start_end["offset_end"] = df_start_end["offset_start"] + df_start_end["paragraph_length"]

            # look-up mapping to match entity types with reference ontologies and
            # controlled vocabularies
            concept_dict = {"chemical" : "CHEBI:",
                            "complex_assembly" : "GO:",
                            "evidence" : "DUMMY:",
                            "experimental_method" : "MESH:",
                            "gene" : "GENE:",
                            "location" : "GO:",
                            "mutant" : "MESH:",
                            "non_covalent_bond" : "MESH:",
                            "oligomeric_state" : "DUMMY:",
                            "protein" : "PR:",
                            "protein_state" : "DUMMY:",
                            "protein_type" : "MESH:",
                            "ptm" : "MESH:",
                            "residue_name" : "SO:",
                            "residue_name_number" : "DUMMY:",
                            "residue_number" : "DUMMY:",
                            "residue_range" : "DUMMY:",
                            "site" : "SO:",
                            "species" : "MESH:",
                            "stoichiometry" : "DUMMY:",
                            "structure_element" : "SO:",
                            "taxonomy_domain" : "DUMMY:",
                            "covalent_bond" : "MESH:",
                            "bond_interaction" : "MESH:"}

            id_counter = 0
            # iterate over the text in the passages for annotations
            for passage in root.iter("passage"):
                # using the offset dataframe to ensure the correct paragraph
                # start and hence character positions for annotations
                offset = int(passage.find("offset").text)
                row = df_start_end.loc[df_start_end['offset_start'] == offset]
                paragraph_start = row["offset_start"].values
                try:
                    if passage.find("text").text is not None:
                        paragraph = passage.find("text").text
                        # set up the model for predictions
                        ner = pipeline("token-classification",
                                    model = model,
                                    tokenizer = tokenizer,
                                    aggregation_strategy = "first")
                        # make predictions with the local model
                        pred = ner([paragraph])
                        logging.info(f"Number of predictions for current passage: {len(pred[0])}")
                except:
                    logging.error(f"Was not able to make predictions with current model {model_name}")
                        
                try:
                    # iterate over the annotations found for the current passage
                    # edit the annotation to be written back into the XML file
                    for ent in pred[0]:
                        # reseting the character start and end position for annotation
                        reset_ent_start = ent['start'] + paragraph_start[0]
                        reset_ent_end = ent['end'] + paragraph_start[0]
                        reset_found = [reset_ent_start, reset_ent_end, paragraph[ent['start']:ent['end']], ent['entity_group'], ent['score']]

                        # using ElementTree to fill the different XML tags so 
                        # annotations adhere to BioC format
                        anno = ET.SubElement(passage, 'annotation', id = str(id_counter))

                        score_val = reset_found[-1]
                        score = ET.SubElement(anno, "infon", key="score")
                        score.text = str(score_val)

                        type_val = reset_found[-2]
                        ent_type = ET.SubElement(anno, 'infon', key="type")
                        ent_type.text = str(type_val)

                        anno_location = ET.SubElement(anno, 'location')
                        offset_val = str(reset_found[0])
                        length_val = str(reset_found[1] - reset_found[0])
                        anno_location.set("offset", offset_val)
                        anno_location.set("length", length_val)

                        text_val = reset_found[2]
                        anno_text = ET.SubElement(anno, 'text')
                        anno_text.text = str(text_val)

                        model_val = model_name
                        anno_model = ET.SubElement(anno, 'infon', key="annotator")
                        anno_model.text = model_val

                        date_val = date
                        anno_date = ET.SubElement(anno, 'infon', key='updated_at')
                        anno_date.text = str(date_val)

                        concept_val = concept_dict[type_val]
                        anno_concept = ET.SubElement(anno, 'infon', key='identifier')
                        anno_concept.text = str(concept_val)

                        id_counter = id_counter + 1
                except:
                    logging.error(f"Passage with offset {offset} does not contain text")
                    continue

            # creating a new tree from the original tree and the annotations
            new_tree = ET.ElementTree(root)

            # defining output file name
            split_1 = file.split(".")
            split_2 = split_1[0].split("_")
            outname = split_2[-1] + "_" + model_name + "_" + date + ".xml"
            out = output_dir + outname

            # writing new BioC formatted XML file with annotations to disk
            with open(out, 'wb') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE collection SYSTEM "BioC.dtd">'.encode('utf8'))
                ET.indent(new_tree, '  ')
                new_tree.write(f, encoding="utf-8")


def main():
    """
    This function annotates BioC formatted XML files of publications for
    named entities using a trained model stored locally. The input
    documents for which annotations are to be produced have to be provided
    through a pointer to the directory where they are kept. All documents
    have to be in BioC formatted XML. It is assumed that input BioC XML
    files have their file names starting with a unique ID, e.g. <PMC ID>,
    which will be reused to construct the output filename. Suggested naming
    convension for input file name is <date>_xml_<unique ID>. A pointer to
    the model locally has to be provided. The model directory name is
    assumed to match the one for the remote location on Huggingface,
    e.g. BiomedNLP-PubMedBERT-ProteinStructure-NER-v2.1.

    Input

    :param xml-dir: directory containing BioC formatted XML files for which
                    annotations are to be created; files are expected to
                    follow a naming convention of <date>_xml_<unique ID>
    :type xml-dir: str()

    :param model-dir: directory containing a trained model for inference;
                      directory name is assumed to match the remote location
                      on Huggingface, e.g. BiomedNLP-PubMedBERT-ProteinStructure-NER-v2.1
    :type model-dir: str()

    :param model-name: model name shorthand to be used as annotator
    :type model-name: str()

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str()


    Output

    :return: <unique ID>_<model name>_<date>.xml; XML file with full text for open access
            publication in BioC format
    :rtype: XML

    """
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = """This function annotates BioC formatted XML files of
                      publications for named entities using a trained model
                      stored locally. The input documents for which annotations
                      are to be produced have to be provided through a pointer
                      to the directory where they are kept. All documents have
                      to be in BioC formatted XML. It is assumed that input BioC
                      XML files have their file names starting with a unique ID,
                      e.g. <PMC ID>, which will be reused to construct the output
                      filename. Suggested naming convension for input file name is
                      <date>_xml_<unique ID>. A pointer to the model locally has to
                      be provided. The model directory name is assumed to match the
                      one for the remote location on Huggingface,
                      e.g. BiomedNLP-PubMedBERT-ProteinStructure-NER-v2.1."""
    )
    parser.add_argument(
                        "--xml-dir",
                        type = str,
                        default = None,
                        dest = "xml_dir",
                        help = "A list of input PMC IDs in TXT format",
    )
    parser.add_argument(
                        "--model-dir",
                        type = str,
                        default = None,
                        dest = "model_dir",
                        help = "local directory of model to be used for inference"
    )
    parser.add_argument(
                        "--model-name",
                        type = str,
                        default = None,
                        dest = "model_name",
                        help = "model name or identifier to be added to predictions as annotator"
    )
    parser.add_argument(
                        "--output-dir",
                        type = str,
                        default = os.getcwd(),
                        dest = "output_dir",
                        help = """output directory to write results files to
                               default = current directory"""
    )

    args = parser.parse_args()

    # parsing the command line input to make the PDBe query for search and filterterms
    run_local_inference_for_ner(args.xml_dir, args.model_dir, args.model_name, args.output_dir)


if __name__ == "__main__":

    main()  
