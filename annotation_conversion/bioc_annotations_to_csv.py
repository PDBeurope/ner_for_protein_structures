# importing necessary modules/libraries
import os
import argparse
import logging
import pandas as pd
from annotation_conversion.xml_processing_tools import get_text_annos_from_xml_as_json
from collections import defaultdict
from tqdm import tqdm

def process_bioc_xml_file(input):
    """
    Extract the annotations from BioC XML file and return the ID of the
    annotated document to be used as identifier and the annotations as a
    nested list. Each element in the list is another list which contains
    for each annotation the start and end character position for the
    annotation, the actual text in the span, the entity type given to the
    text span, the sentence the annotation was found in and the section
    of the publication the sentence belongs to.

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

    full_anno_list = []
    for _, k in enumerate(non_overlap.keys()):
        span_list = []
        sect_list = []
        for a in non_overlap[k]:
            char_start = a[0]
            char_end = a[1]
            covered_span = a[2]
            ent_type = a[3]
            sect = a[4]
            found_ann = [char_start, char_end, covered_span, ent_type, k]
            span_list .append(found_ann)
            sect_list.append(sect)
        sect_list_unique = list(set(sect_list))

        try:
            assert len(sect_list_unique) == 1
            for s in span_list:                
                anno_full = s + sect_list_unique
                full_anno_list.append(anno_full)
                
        except:
            logging.warning(f"""Found multiple entries for same sentence and
                           annotation; only using first occurance""")
            for s in span_list:
                anno_full = s + [sect_list_unique[0]]
                full_anno_list.append(anno_full)
        pass

    assert len(full_anno_list) == non_overlap_counter
    
    logging.info(f"""Total number of annotations processed for current
                publication: {non_overlap_counter}""")
    logging.info(f"""Total number of sentences processed for current
                publication: {len(non_overlap)}""")
    logging.info(f"*" * 80)

    return doc_id, full_anno_list


def make_annotation_csv(bioc_xml_dir, output_dir):
    """
    Iterate over the annotations in the returned list for the document and
    convert into a dataframe to save as tab-separated CSV file to disk

    """

    progress_bar_pub = tqdm(total=len(os.listdir(bioc_xml_dir)),
                                 desc = "Iterating over publications...")
    
    for file in os.listdir(bioc_xml_dir):
        if file.endswith(".xml"):
            logging.info(f"Processing file {file}")
            input = os.path.join(bioc_xml_dir, file)
        
            doc_id, sent_anno_list = process_bioc_xml_file(input)

            columns = ["anno_start", "anno_end", "anno_text", "entity_type", "sentence", "section"]
            df = pd.DataFrame(sent_anno_list, columns = columns)

            full_out_path = output_dir
            output_csv = full_out_path + doc_id + ".csv"

            with open(output_csv, 'w') as f:
                f.write(df.to_csv(sep='\t', index=False))
        progress_bar_pub.update()

        
def main():

    """

    This script extracts the annotations from a BioC formatted XML file along
    with the sentence they belong to and writes them into a tab-separated CSV
    file with the following column labels: anno_start, anno_end, anno_text,
    entity_type, sentence, section; one one CSV file for each XML file

    Input

    :param bioc-xml-dir: location of directory holding BioC XML files with annotations

    :type bioc-xml-dir: str()

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str()


    Output

    :return: <doc_id>.csv
    :rtype: CSV 

    """

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description = """This script extracts the annotations from a BioC
                      formatted XML file along with the sentence they belong
                      to and writes them into a tab-separated CSV file with
                      the following column labels: anno_start, anno_end,
                      anno_text, entity_type, sentence, section; one one CSV
                      file for each XML file"""
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

    # parsing the command line input
    make_annotation_csv(args.bioc_xml_dir, args.output_dir)
    

if __name__ == "__main__":

    main()