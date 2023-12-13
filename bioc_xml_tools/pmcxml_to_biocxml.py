
import os
import logging
from datetime import datetime
import argparse
import bioc
from bioconverters import pmcxml2bioc


logger = logging.getLogger(__name__)


def pmcxml_to_biocxml(pmcxml_dir, output_dir):
    print(output_dir)

    for x in os.listdir(pmcxml_dir):
        if x.endswith("xml"):
            xml = pmcxml_dir + x

            print(xml)

            xml_name = x.strip(".xml")
            print(xml_name)

            for doc in pmcxml2bioc(xml, mark_citations = False):
                print(80 * "*")
                print(80 * "*")
                print(80 * "*")
                print(doc)
                # modified BioCXMLDocumentWriter in /bioc/bioxml/encoder.py to add hyphen to fix utf-8 declaration
                out_name = output_dir + xml_name + "_bioc.xml"

                print(out_name)

                out_bioc_handle = bioc.BioCXMLDocumentWriter(out_name)

                out_bioc_handle.write_document(doc)
                out_bioc_handle.close()





def main():
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = "Parsing a directory path to a folder containing PDF files with \n"
                      "highlighted text. The files are expected to be named with their \n"
                      "corresponding PubMed ID for easier tracking. Any PDF file can be \n"
                      "analysed but it is assumed that the literature represents open \n"
                      "access publications from PubMed/EuropePMC. Highlighted text \n"
                      "passages will be extracted and combined with its PubMed ID in a \n"
                      "dictionary. After iterating over all files in the directory a \n"
                      "JSON file containing nested dictionaries for all files is returned."
    )
    parser.add_argument(
                        "--pmcxml-dir",
                        type = str,
                        default = None,
                        dest = "pmcxml_dir",
                        help = "Path to directory containing PDF files with highlighted\n"
                               "text passages. The files are expected to have their \n"
                               "corresponding PubMed ID as filename for easier tracking."
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

    # parsing the command line input to make Wikipedia request for a page
    pmcxml_to_biocxml(args.pmcxml_dir, args.output_dir)


if __name__ == "__main__":

    main()  