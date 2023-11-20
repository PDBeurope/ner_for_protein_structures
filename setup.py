from setuptools import setup

VERSION = {}
# __version__.py defines VERSION and VERSION_SHORT variables.
# We use exec here to read it so that we don't import scispacy
# whilst setting up the package.
with open("__version__.py", "r") as version_file:
    exec(version_file.read(), VERSION)

setup(name = "ner_for_protein_structures",
    version = VERSION["VERSION"],
    description = "Module",
    author = "Melanie Vollmar",
    author_email = "melaniev@ebi.ac.uk",
    license="Apache 2.0",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            # "ner_for_protein_structures.get_bioc_xml_from_pmc = bioc_xml_retrieval.get_bioc_xml_from_pmc:main",
            # "ner_for_protein_structures.process_bioc_xml_for_training = annotation_conversion.process_bioc_xml_for_training:main",
            # "ner_for_protein_structures.process_bioc_xml_for_performance_stats = annotation_conversion.process_bioc_xml_for_performance_stats:main",
            # "ner_for_protein_structures.bioc_annotations_to_json = annotation_conversion.bioc_annotations_to_json:main",
            "ner_for_protein_structures.bioc_annotations_to_csv = annotation_conversion.bioc_annotations_to_csv:main",
            # "ner_for_protein_structures.run_semeval_analysis = sem_eval.run_semeval_analysis:main",
            # "ner_for_protein_structures.run_hf_inference_for_ner = ner_inference.run_hf_inference_for_ner:main",
            # "ner_for_protein_structures.run_local_inference_for_ner = ner_inference.run_local_inference_for_ner:main",
            ]
        }
    )
