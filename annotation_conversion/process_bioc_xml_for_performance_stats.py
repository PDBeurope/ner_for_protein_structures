# importing necessary modules/libraries
import os
import argparse
import logging
from annotation_conversion.xml_processing_tools import get_text_annos_from_xml_for_selected_sections
from annotation_conversion.xml_processing_tools import convert_all_to_IOB
from collections import defaultdict
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def process_bioc_xml_file(bioc_xml_dir, output_dir, annotator = None):
    """
    opening a BioC XML file with annotations and extracting all the annotations
    and their corresponding sentences in a document; alternatively add identifiers
    for individual annotators; convert the sentences and their annottaions to IOB
    format for analysis with SemEval script
    """
    non_overlap = defaultdict(list)
    non_overlap_counter = 0
    progress_bar_pub = tqdm(total=len(os.listdir(bioc_xml_dir)),
                                 desc = "Iterating over publications...")
    for file in os.listdir(bioc_xml_dir):
        prev_sent_len = len(non_overlap)
        if file.endswith(".xml"):
            print("*" * 80)
            logger.info(f"Processing annotated publication {file}")
            input = os.path.join(bioc_xml_dir, file)

            text_list, anno_list = get_text_annos_from_xml_for_selected_sections(input, annotator)

            current_non_overlap_counter = 0

            # for each_annotation in anno_list:
            for each_annotation in anno_list:
                # get start of annotation span
                st_ann_sp = int(each_annotation["anno_start"])
                # get end of annotation span
                en_ann_sp = int(each_annotation["anno_end"])
                # get annotation type for span
                ann_type = each_annotation["anno_type"]
                # get the text of the annotation span
                ann = each_annotation["anno_text"]
                
                
                # iterate over the individual sentences in in the flattened text span list
                for each_text in text_list:
                    # get the sentence raw text
                    snt_text = str(each_text[0])        
                    # get the start of the sentence span
                    st_snt_sp = int(each_text[1])        
                    # get the end of the sentence span
                    en_snt_sp = int(each_text[2])
                        
                    # check if the annotation span is within the sentence span 
                    if st_snt_sp <= st_ann_sp <= en_snt_sp and st_snt_sp <= en_ann_sp <= en_snt_sp:
                        # process only if the annotation is in the sentence
                        if ann in snt_text: 
                            # get the annotation details and assemble so it can be added to the
                            # appropriate dict below
                            anno_list_ext = [st_ann_sp-st_snt_sp, en_ann_sp-st_snt_sp, ann, ann_type]
                            # final check if annotation is indeed in the text and has the right span
                            found_span = snt_text[st_ann_sp-st_snt_sp:en_ann_sp-st_snt_sp]

                            if found_span == ann:
                                non_overlap[snt_text].append(anno_list_ext)
                                current_non_overlap_counter = current_non_overlap_counter + 1

                            # check for leading white spaces and other oddities and clean them up
                            elif found_span.startswith(" "):
                                st_ann_sp_new = st_ann_sp + 1
                                en_ann_sp_new = en_ann_sp + 1
                                # logger.info(f"Reset annotation span to eliminate leading white space for annotation:")
                                # cur_anno = (snt_text[st_ann_sp_new-st_snt_sp:en_ann_sp_new-st_snt_sp], ann)
                                # logger.info(cur_anno)
                                anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type]
                                non_overlap[snt_text].append(anno_list_ext)
                                current_non_overlap_counter = current_non_overlap_counter + 1
                            elif found_span.startswith("("):
                                st_ann_sp_new = st_ann_sp + 1
                                en_ann_sp_new = en_ann_sp + 1
                                # logger.info(f"Reset annotation span to eliminate leading parenthesis for annotation:")
                                # cur_anno = (snt_text[st_ann_sp_new-st_snt_sp:en_ann_sp_new-st_snt_sp], ann)
                                # logger.info(cur_anno)
                                anno_list_ext = [st_ann_sp_new-st_snt_sp, en_ann_sp_new-st_snt_sp, ann, ann_type]
                                non_overlap[snt_text].append(anno_list_ext)
                                current_non_overlap_counter = current_non_overlap_counter + 1
                            else:
                                logger.info(f"Could not resolve annotation")
                                # cur_anno = (found_span, ann)
                                # logger.info(cur_anno)
                                # logger.info(f"Start found for annotation span {st_ann_sp}")
                                # logger.info(f"Start found for sentence span {st_snt_sp}")
                                # logger.info(f"End found for annotation span {en_ann_sp}")
                                # logger.info(f"End found for sentence span {en_snt_sp}")
                                continue

            logger.info(f"Number of annotations after processing: {current_non_overlap_counter}")
        
        cur_doc_sent = len(non_overlap) - prev_sent_len
        logger.info(f"Number of sentences after processing: {cur_doc_sent}")
        progress_bar_pub.update()
        print("")

    print("*" * 80)
    # get all the non-overlapping annotations
    len_non_overlap = len(non_overlap)
    logger.info(f"Total number of sentences with annotations across all publications: {len_non_overlap}")
    for key in non_overlap.keys():
        anno_all_length = len(non_overlap[key])
        non_overlap_counter = non_overlap_counter + anno_all_length
    logger.info(f"Total number of annotations across all publications: {non_overlap_counter}")

    full_out_path = output_dir
    convert_all_to_IOB(non_overlap, full_out_path)



def main():
    """
    This script extracts the annotations from a BioC formatted XML file along
    with the sentence they belong to and converts everything into IOB
    formatted sentences with annotations; IOB formatted annotations serve as
    input for calculating performance statistics following the SemEval
    procedure; optionally, an 'annotator' can be selected for later calculation
    of individual performance for either a human annotator or predictions
    from a trained model; a tab-separated TSV files 'all.tsv' acontains
    all annotated sentences; 

    Input

    :param pmcid-list: full path to BioC formatted XML files with annotations
    :type pmcid-list: str

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str

    :param annotator: lable/name/identifier for a particular human annotator or
                      trained model
    :type annotator: str

    
    Output

    :return: all.tsv; tab-separated TSV file of relevant sentences and their
             annotations in IOB format
    :rtype: TSV

    """
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = "This script extracts the annotations from a BioC formatted \n"
                      "XML file along with the sentence they belong to and converts \n"
                      "everything into IOB formatted sentences with annotations; \n"
                      "IOB formatted annotations serve as input for calculating \n"
                      "performance statistics following the SemEval procedure; \n"
                      "optionally, an 'annotator' can be selected for later \n"
                      "calculation of individual performance for either a human \n"
                      "annotator or predictions from a trained model"
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
                        help = "output directory to write results files to; \n"
                               "default = current directory"
    )
    parser.add_argument(
                        "--annotator",
                        type = str,
                        default = None,
                        dest = "annotator",
                        help = "name of annotator to use for getting annotation stats for; \n"
                               "default = None"
    )

    args = parser.parse_args()

    # parsing the command line input to make the PDBe query for search and filterterms
    process_bioc_xml_file(args.bioc_xml_dir, args.output_dir, args.annotator)
    

if __name__ == "__main__":

    main()  
       