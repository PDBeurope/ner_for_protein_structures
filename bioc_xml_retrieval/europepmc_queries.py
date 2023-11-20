#! /Users/melaniev/Documents/code/ner_for_protein_structure/ner_venv/bin/python

# importing necessary modules/libraries
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_bioc_xml(pmcid):
    """
    Fetch BioC formated XML files for fulltext open access articles from
    NCBI's BioNLP group RESTful API.

    Input

    :param pmcid: single PMCID
    :type pmcid: str


    Output

    :return: <currentdate>_xml_<unique PubMedCebtral ID>.xml; BioC formatted XML
    :rtype: XML

    """

    base_url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/"
    query = base_url + pmcid + "/unicode"

    result = requests.get(query)

    if result.ok:
        return result
    else:
        logger.error(f"Query returned no result")

