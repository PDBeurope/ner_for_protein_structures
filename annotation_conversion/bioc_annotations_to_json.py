# importing necessary modules/libraries
import os
import argparse
import logging
import json
from annotation_conversion.xml_processing_tools import get_text_annos_from_xml_as_json
from collections import defaultdict
from tqdm import tqdm

def process_bioc_xml_file(input):
    """
    Extract the annotations from BioC XML file and return the ID of the
    annotated document to be used as identifier and the annotations as a
    list of JSON dictionaries. Each element in the list is a JSON dictionary
    which represents a sentence. The keys for the dictionary are sid, sent,
    section and ner. Ner represents a nested list for all the annotations
    found in the sentence of sid and each sublist contains the start and end
    character positions of an annotation, the text snippet under the covered
    span and the entity type.

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
                        anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type, doc_section]
                        non_overlap[snt_text].append(anno_list_ext)
                        non_overlap_counter = non_overlap_counter + 1
                    elif found_span.startswith("("):
                        st_ann_sp_new = st_ann_sp + 1
                        en_ann_sp_new = en_ann_sp + 1
                        anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type, doc_section] 
                        non_overlap[snt_text].append(anno_list_ext)
                        non_overlap_counter = non_overlap_counter + 1
                    else:
                        logging.info(f"Could not resolve annotation")
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
            logging.info(f"""Found multiple entries for same sentence and
                         annotation; only using first occurance""")
            sent_dict = {"sid" : i,
                    "sent" : k,
                    "section" : sect_list_unique[0],
                    "ner" : span_list}
            sent_anno_list.append(sent_dict)
        pass

    assert len(sent_anno_list) == len(non_overlap)
    
    logging.info(f"""Total number of annotations processed for current
                 publication: {non_overlap_counter}""")
    logging.info(f"""Total number of sentences processed for current
                 publication: {len(non_overlap)}""")
    logging.info(f"*" * 80)

    return doc_id, sent_anno_list


def make_annotation_json(bioc_xml_dir, output_dir):
    """
    Iterate over the annotations in the returned list for the document and
    create a combined JSON file to save to disk

    """
    progress_bar_pub = tqdm(total=len(os.listdir(bioc_xml_dir)),
                                 desc = "Iterating over publications...")

    doc_dict = {}

    for file in os.listdir(bioc_xml_dir):
        if file.endswith(".xml"):
            logging.info(f"Processing file {file}")
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

    """

    This script extracts the annotations from a BioC formatted XML file along
    with the sentence they belong to. All the documents in a given directory
    are processed and their respective IDs, <unique PubMedCentral ID>, are
    used as key in the returned JSON dictionary. For each document entry the
    following keys are used for the annotations: annotations, sid, sent,
    section, ner. 'ner' contains a list of annotations for the sentence with
    ID sid. All documents and their annotations are saved to disk as
    annotations.json.

    Input

    :param bioc-xml-dir: location of directory holding BioC XML files with annotations

    :type bioc-xml-dir: str()

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str()


    Output

    :return: annotations.json
    :rtype: {JSON}

    """

    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = """This script extracts the annotations from a BioC
                      formatted XML file along with the sentence they
                      belong to and writes them into a JSON file with the
                      following keys: '<unique PubMedCentral ID>',
                      'annotations', 'sid', 'sent', 'section', 'ner'; 'ner'
                      contains a list of annotations for the sentence with ID
                      'sid'"""
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
                        help = """output directory to write results files to
                               default = current directory"""
    )

    args = parser.parse_args()

    # parsing the command line input to make the PDBe query for search and filterterms
    make_annotation_json(args.bioc_xml_dir, args.output_dir)
    

if __name__ == "__main__":

    main()