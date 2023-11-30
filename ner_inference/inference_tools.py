# importing necessary modules/libraries
import requests


def make_hf_request(model_repo, auth_token, payload):
    """
    Make a request to Huggingface inference API and retrieve
    predictions for named entities

    Input

    :param model_repo: Huggingface model name
    :type model_repo: str()

    :param auth_token: Huggingface authentication token
    :type auth_token: str()

    :param payload: dictionary containing the following query details:
                    {"inputs": str(),
                     "wait_for_model": True,
                     "aggregation_strategy" : "first",}
                     where inputs represents the input text as string for which
                     predictions are to be made
    :type payload: dict{}

    Output

    :return: <currentdate>_xml_<unique PubMedCebtral ID>.xml; BioC formatted XML
    :rtype: XML

    """
    # basic URL to Huggingface API
    hf_url = "https://api-inference.huggingface.co/models/"
    # expanded URL to point at repo
    hf_repo = hf_url + model_repo
    # creating the headers for request
    headers = {"Authorization": f"Bearer {auth_token}"}
    # making a Huggingface request through API
    response = requests.post(hf_repo, headers = headers, json = payload)

    return response.json()
