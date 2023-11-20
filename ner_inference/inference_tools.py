#! /Users/melaniev/Documents/code/ner_for_protein_structures/ner_venv/bin/python

import requests


def make_hf_request(model_repo, auth_token, payload):
    # basic URL to Huggingface API
    hf_url = "https://api-inference.huggingface.co/models/"
    # expanded URL to point at repo
    hf_repo = hf_url + model_repo
    # creating the headers for request
    headers = {"Authorization": f"Bearer {auth_token}"}
    # making a Huggingface request through API
    response = requests.post(hf_repo, headers=headers, json=payload)

    return response.json()
