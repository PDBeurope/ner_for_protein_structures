# importing necessary modules/libraries
import argparse
import os
import logging
from datetime import datetime
from pathlib import Path
from bioc_xml_tools.europepmc_queries import fetch_bioc_xml

def get_bioc_xml_from_pmc(pmcid_list, output_dir):
    """
    making a request to open access set at NCBI to retrieve BioC formatted XML
    for a given PMC ID
    """
    try:
        # ckeck whether the input file (list of PMCIDs) exists
        input_file = Path(pmcid_list)
        assert input_file.exists()
    except:
        logging.error(f"No input file found")
        pass
    # open the input file (list of PMCIDs)
    with open(input_file, "r") as f:
        input_list = f.readlines()
    logging.info(f"Number of unique entries to fetch full text XML for: {len(input_list)}")
    # iterate over list of PMC IDs and make a request to NCBI BioNLP API to get
    # the XML text
    counter = 0
    for pmcid in input_list:
        pmcid = pmcid.strip("\n")
        # make the request; this returns the full
        # text XML where open access is true
        try:
            result = fetch_bioc_xml(pmcid)
            counter = counter + 1
            # create an output filepath and name to write the search results to disk; add time stamp
            date = datetime.strftime(datetime.now(), "%Y%m%d")
            output = output_dir + "/" + date + "_xml_" + str(pmcid) + ".xml"
            with open(output, "wb") as f:
                f.write(result.content)
        except:
            # return an error if there is no open access XML found for a given PMC ID
            logging.error(f"Could not get full text XML")
            pass
    logging.info(f"Final number of PubMed IDs processed: {counter}")

    # return the list of dictionaries
    return


def main():
    """
    This function uses a list of PMC IDs in TXT format as input to query 
    NCBI BioNLP API and retrieve the full text BioC formated XML for each ID. 
    This is only possible if a given ID represents an open access publication. 
    If access is restricted in any way, then the full text can not be retrieved. 
    The returned XML file contains the publication text formated according to
    BioC XML standards as develop by the BioCreative initiative.

    Input

    :param pmcid-list: list of PMC IDs representing open access, full text 
                       publications in PMC; in TXT format
    :type pmcid-list: list[str]

    :param output-dir: full path to output directory; default = current directory
    :type output-dir: str


    Output

    :return: <date>_xml_<PMCID>.xml; XML file with full text for open access
            publication in BioC format
    :rtype: XML

    """
     
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = """Parsing a list PMC IDs in TXT format to retrieve
                      their associated full text XML by querying NCBI BioNLP API.
                      Returns an XML file in BioC format for each PMC ID if the
                      access for the ID is open."""
    )
    parser.add_argument(
                        "--pmcid-list",
                        type = str,
                        default = None,
                        dest = "pmcid_list",
                        help = "A list of input PMC IDs in TXT format",
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
    get_bioc_xml_from_pmc(args.pmcid_list, args.output_dir)


if __name__ == "__main__":

    main()  