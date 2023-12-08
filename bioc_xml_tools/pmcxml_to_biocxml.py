#!/usr/bin/env python3

import bioc
from bioconverters import pmcxml2bioc




for doc in pmcxml2bioc('./d-79-00735.xml', mark_citations=False):
    out_bioc_handle = bioc.BioCXMLDocumentWriter('./d-79-00735.bioc.xml') # modified BioCXMLDocumentWriter in /bioc/bioxml/encoder.py to add hyphen to fix utf-8 declaration
    out_bioc_handle.write_document(doc)
    out_bioc_handle.close()

'''
import xml.etree.ElementTree as ET
tree = ET.parse('./d-79-00735.bioc.xml')
root = tree.getroot()
'''
