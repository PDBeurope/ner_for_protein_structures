#! /Users/melaniev/Documents/code/ner_for_protein_structure/ner_venv/bin/python

# importing necessary modules/libraries

import os
import argparse
import logging
import json
from annotation_conversion.xml_processing_tools import get_text_annos_from_xml_as_json
from collections import defaultdict
from tqdm import tqdm


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def process_bioc_xml_file(input):
    """
    This script extracts the annotations from a BioC formatted XML file along
    with the sentence they belong to and writes them into a JSON
    file with the following keys: '<unique PubMedCentral ID>', 'annotations',
    'sid', 'sent', 'section', 'ner'; 'ner' contains a list of annotations for the sentence
    with ID 'sid'

    Input

    :param pmcid-list: full path to BioC formatted XML files with annotations
    :type pmcid-list: str

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str


    Output

    :return: <unique PubMedCentral ID>.csv; tab-separated CSV file of relevant
             sentences and their annotations; column labels are: anno_start,
             anno_end, anno_text, entity_type, sentence, section
    :rtype: str

    """
    non_overlap = defaultdict(list)
    non_overlap_counter = 0

    doc_id, text_list, anno_list = get_text_annos_from_xml_as_json(input)

    # iterate over the individual sentences in in the flattened text span list
    for each_annotation in anno_list:
        # get start of annotation span
        st_ann_sp = int(each_annotation["anno_start"])
        # get end of annotation span
        en_ann_sp = int(each_annotation["anno_end"])
        # get annotation type for span
        ann_type = each_annotation["anno_type"]
        # get the text of the annotation span
        ann = each_annotation["anno_text"]


        for each_text in text_list:
            # get the sentence raw text
            snt_text = str(each_text[0])        
            # get the start of the sentence span
            st_snt_sp = int(each_text[1])        
            # get the end of the sentence span
            en_snt_sp = int(each_text[2])
            # get document section for sentence
            doc_section = str(each_text[3])


            # check if the annotation span is within the sentence span 
            if st_snt_sp <= st_ann_sp <= en_snt_sp and st_snt_sp <= en_ann_sp <= en_snt_sp:
                # process only if the annotation is in the sentence
                if ann in snt_text: 
                    # get the annotation details and assemble so it can be added to the
                    # appropriate dict below
                    anno_list_ext = [st_ann_sp-st_snt_sp, en_ann_sp-st_snt_sp, ann, ann_type, doc_section]
                    # final check if annotation is indeed in the text and has the right span
                    found_span = snt_text[st_ann_sp-st_snt_sp:en_ann_sp-st_snt_sp]

                    
                    if found_span == ann:
                        # adding sentence and respective annotations to non_overlap dictionary
                        non_overlap[snt_text].append(anno_list_ext)
                        non_overlap_counter = non_overlap_counter + 1

                    # check for leading white spaces and other oddities and clean them up
                    elif found_span.startswith(" "):
                        st_ann_sp_new = st_ann_sp + 1
                        en_ann_sp_new = en_ann_sp + 1
                        # logger.info(f"Reset annotation span to eliminate leading white space for annotation:")
                        # cur_anno = (snt_text[st_ann_sp_new-st_snt_sp:en_ann_sp_new-st_snt_sp], ann)
                        # logger.info(cur_anno)
                        anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type, doc_section]
                        non_overlap[snt_text].append(anno_list_ext)
                        non_overlap_counter = non_overlap_counter + 1
                    elif found_span.startswith("("):
                        st_ann_sp_new = st_ann_sp + 1
                        en_ann_sp_new = en_ann_sp + 1
                        # logger.info(f"Reset annotation span to eliminate leading parenthesis for annotation:")
                        # cur_anno = (snt_text[st_ann_sp_new-st_snt_sp:en_ann_sp_new-st_snt_sp], ann)
                        # logger.info(cur_anno)
                        anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type, doc_section] 
                        non_overlap[snt_text].append(anno_list_ext)
                        non_overlap_counter = non_overlap_counter + 1
                    else:
                        logger.info(f"Could not resolve annotation")
                        # cur_anno = (found_span, ann)
                        # logger.info(cur_anno)
                        # logger.info(f"Start found for annotation span {st_ann_sp}")
                        # logger.info(f"Start found for sentence span {st_snt_sp}")
                        # logger.info(f"End found for annotation span {en_ann_sp}")
                        # logger.info(f"End found for sentence span {en_snt_sp}")
                        continue

    sent_anno_list = []
    for i, k in enumerate(non_overlap.keys()):
        span_list = []
        sect_list = []
        for a in non_overlap[k]:
            char_start = a[0]
            char_end = a[1]
            covered_span = a[2]
            ent_type = a[3]
            sect = a[4]
            found_ann = [char_start, char_end, covered_span, ent_type]
            span_list .append(found_ann)
            sect_list.append(sect)
        sect_list_unique = list(set(sect_list))

        try:
            assert len(sect_list_unique) == 1
            sent_dict = {"sid" : i,
                "sent" : k,
                "section" : sect_list_unique[0],
                "ner" : span_list}
            sent_anno_list.append(sent_dict)

        except:
            logger.info(f"Found multiple entries for same sentence and annotation; only using first occurance")
            sent_dict = {"sid" : i,
                    "sent" : k,
                    "section" : sect_list_unique[0],
                    "ner" : span_list}
            sent_anno_list.append(sent_dict)
        pass

    assert len(sent_anno_list) == len(non_overlap)
    
    logger.info(f"Total number of annotations processed for current publication: {non_overlap_counter}")
    logger.info(f"Total number of sentences processed for current publication: {len(non_overlap)}")
    logger.info(f"*" * 80)

    return doc_id, sent_anno_list


def make_annotation_json(bioc_xml_dir, output_dir):
    progress_bar_pub = tqdm(total=len(os.listdir(bioc_xml_dir)),
                                 desc = "Iterating over publications...")

    doc_dict = {}

    for file in os.listdir(bioc_xml_dir):
        if file.endswith(".xml"):
            logger.info(f"Processing file {file}")
            input = os.path.join(bioc_xml_dir, file)
        
            doc_id, sent_anno_list = process_bioc_xml_file(input)

            doc_dict[doc_id] = {"annotations" : sent_anno_list}
        progress_bar_pub.update()
    
    full_out_path = output_dir
    output_json = full_out_path + "annotations.json"

     # Serializing json
    json_object = json.dumps(doc_dict, indent=4)

    # Writing to sample.json
    with open(output_json, "w") as outfile:
        outfile.write(json_object)


        

def main():
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = "This script extracts the annotations from a BioC \n"
                      "formatted XML file along with the sentence they \n"
                      "belong to and writes them into a JSON file with the \n"
                      "following keys: '<unique PubMedCentral ID>', \n"
                      "'annotations', 'sid', 'sent', 'section', 'ner'; 'ner' \n"
                      "contains a list of annotations for the sentence with ID \n"
                      "'sid'"
    )
    parser.add_argument(
                        "--bioc-xml-dir",
                        type = str,
                        default = None,
                        dest = "bioc_xml_dir",
                        help = "location of directory holding BioC XML files with annotations",
    )
    parser.add_argument(
                        "--output-dir",
                        type = str,
                        default = os.getcwd(),
                        dest = "output_dir",
                        help = "output directory to write results files to \n"
                            "default = current directory"
    )

    args = parser.parse_args()

    # parsing the command line input to make the PDBe query for search and filterterms
    make_annotation_json(args.bioc_xml_dir, args.output_dir)
    

if __name__ == "__main__":

    main()