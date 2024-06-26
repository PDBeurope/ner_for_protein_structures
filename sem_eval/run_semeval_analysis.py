# importing necessary modules/libraries
import argparse
import os
import logging
from datetime import datetime
from pathlib import Path
from sem_eval.performance_stats_from_IOB_pred_gt import semeval_report

def run_semeval_analysis(iob_gt, iob_ann, validate_labels, entity_types, output_dir):
    """
    open the various input files and check they exist; run SemEval evaluation and compare
    ground truth annotations in IOB format with manually/automatically annotated text in
    IOB format to get annotation statistics and performance
    """
    try:
        # ckeck whether the input file (list of PMCIDs) exists
        gt_input = Path(iob_gt)
        assert gt_input.exists()
    except:
        logging.error(f"No input file found")
        pass

    try:
        # ckeck whether the input file (list of PMCIDs) exists
        ann_input = Path(iob_ann)
        assert ann_input.exists()
    except:
        logging.error(f"No annotated file found")
        pass

    try:
        # ckeck whether the input file (list of PMCIDs) exists
        ent_types = Path(entity_types)
        assert ent_types.exists()
        with open(ent_types) as ent:
            ent_list = ent.readlines()
    except:
        logging.error(f"No input file with entity types found")
        pass

    try:
        ent_list_clean = []
        for e in ent_list:
            if "\n" in e:
                e_stripped = e.strip("\n")
                ent_list_clean.append(e_stripped)
    except:
        pass

    try:
        report = semeval_report(gold_path = gt_input, response_path = ann_input,
                       validate_label = validate_labels, targets = ent_list_clean)
        logging.info(f"Finished evaluation")
    except:
        logging.error(f"Could not get scores")
        pass

    try:
        date = datetime.strftime(datetime.now(), "%Y%m%d")
        output = output_dir + "/" + date + "_SemEval_report.txt"
        with open(output, "w") as f:
            f.write(report)
    except:
        logging.error(f"Could not write output")
        pass

def main():
    """
    This function runs the SemEval evaluation script to calculate performance
    statistics as precision, recall and F1 measure for annotations coming from
    either an automatic system in form of predictions, or as manually created
    annotations. The details for the evaluation process have been published here:
    https://aclanthology.org/S13-2056.pdf. Two IOB formatted input files of
    word tokesn and corresponding labels have to be provided. One of the files
    represents the ground truth/gold standard to compare against. The other one
    contains the predicted/manually created annotations.

    Input

    :param ground-truth-IOB: path to IOB formated sentence input of word tokens 
                             and labels for the ground truth/gold standard data;
                             tab-separated .TSV/.CSV file
    :type ground-truth-IOB: str

    :param annotated-IOB: path to IOB formated sentence input of word tokens
                          and labels for the predicted/manually created data;
                          tab-separated .TSV/.CSV file
    :type annotated-IOB: str

    :param validate-labels: True/False Boulean label on whether or not to check
                            label integrity; default: True
    :type validate-labels: Boulean

    :param entity-types: path to .TXT file containg the entity type labels that
                         were used to generate the IOB formatted data files
    :type entity-types: str
    
    :param output-dir: full path to output directory; default: current directory
    :type output-dir: str


    Output

    :return: <current date>_SemEval_report.txt; text file containing the score
             report for matches in annotations between the ground truth/gold
             standard and the predicted/manually created data following the
             SemEval scoring procedure.
    :rtype: str

    """

    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        description = """This tool runs the SemEval evaluation script to calculate
                      performance statistics as precision, recall and F1 measure
                      for annotations coming from either an automatic system in
                      form of predictions, or as manually created annotations.
                      The details for the evaluation process have been published
                      here: https://aclanthology.org/S13-2056.pdf. Two IOB
                      formatted input files of word tokesn and corresponding
                      labels have to be provided. One of the files represents
                      the ground truth/gold standard to compare against. The
                      other one contains the predicted/manually created annotations."""
    )
    parser.add_argument(
                        "--ground-truth-IOB",
                        type = str,
                        default = None,
                        dest = "iob_gt",
                        help = """path to tab-separated ground truth CSV file
                               containing sentences and annotations in IOB format"""
    )
    parser.add_argument(
                        "--annotated-IOB",
                        type = str,
                        default = None,
                        dest = "iob_ann",
                        help = """path to tab-separated CSV file to compare against
                               ground truth containing sentences and annotations
                               in IOB format"""
    )
    parser.add_argument(
                        "--validate-labels",
                        type = str,
                        default = None,
                        dest = "validate_labels",
                        help = """True/False Boulean label on whether or not to
                               check label integrity; default: True"""
    )
    parser.add_argument(
                        "--entity-types",
                        type = str,
                        default=None,
                        dest = "entity_types",
                        help = """path to .TXT file containg the entity type
                               labels that were used to generate the IOB
                               formatted data files"""
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
    run_semeval_analysis(args.iob_gt, args.iob_ann, args.validate_labels, args.entity_types, args.output_dir)


if __name__ == "__main__":

    main()  