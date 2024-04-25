# importing necessary modules/libraries
import os
import logging
import argparse
import bioc
from bioconverters import pmcxml2bioc

def pmcxml_to_biocxml(pmcxml_dir, output_dir):
    """Converting EuropePMC/JATS style XML files into BioC style XML files.
    Note: bioc library is version <2.1"""

    for x in os.listdir(pmcxml_dir):
        if x.endswith("xml"):
            xml = pmcxml_dir + x
            xml_name = x.strip(".xml")
            for doc in pmcxml2bioc(xml, mark_citations = False):
                # modified BioCXMLDocumentWriter in /bioc/bioxml/encoder.py to add hyphen to fix utf-8 declaration
                out_name = output_dir + xml_name + "_bioc.xml"

                out_bioc_handle = bioc.BioCXMLDocumentWriter(out_name)

                out_bioc_handle.write_document(doc)
                out_bioc_handle.close()



def main():
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = """Converting EuropePMC/JATS style XML files into
                      BioC style XML files. Note: this relies on the bioc
                      library with version <2.1"""
    )
    parser.add_argument(
                        "--pmcxml-dir",
                        type = str,
                        default = None,
                        dest = "pmcxml_dir",
                        help = """Path to directory containing EuropePMC or JATS style
                               XML files"""
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

    # parsing the command line input to make Wikipedia request for a page
    pmcxml_to_biocxml(args.pmcxml_dir, args.output_dir)


if __name__ == "__main__":

    main()  