# importing necessary modules/libraries
import csv
import logging
import pandas as pd
from operator import add
from collections import namedtuple
from typing import List, Tuple, Dict


"""
Date: 13 Nov. 2019
Author: Xiao Yang <yangx@ebi.ac.uk>

evaluation metrics using https://aclanthology.org/S13-2056.pdf
with 4 metrics:

1. Strict evaluation
2. Exact boundary matching: regardless to the type
3. Partial boundary matching: regardless to the type
4. Type matching: some overlap is required

Correct (COR) : the system's output and the gold-standard annotation agree.
Incorrect (INC) : the system's output and the gold-standard annotation disagree.
Partial (PAR) : the systems' output and the gold-standard annotation are not identical but have some overlapping text. 
Only if partial is allowed.
Missing (MIS) : there is a golden annotation that is not identified by the system.
Spurius (SPU) : the system labels an entity that does not exist in the gold-standard.

"""

Entity = namedtuple('Entity', ['span', 'tag'])
Entity_Label = namedtuple('Label', ['index', 'pos', 'tag'])


class MatchCount:
    """
    class to record the count of matching annotations between ground truth and
    predicted or manually created annotations
    """
    def __init__(self, correct=0, incorrect=0, partial=0, missing=0, spurious=0):
        self.correct = correct
        self.incorrect = incorrect
        self.partial = partial
        self.missing = missing
        self.spurious = spurious

    def __eq__(self, other: 'MatchCount'):
        """
        check the equality by attribute values
        """
        if not isinstance(other, MatchCount):
            return NotImplemented
        isequal = self.correct == other.correct and self.incorrect == other.incorrect and \
            self.partial == other.partial and self.missing == other.missing and self.spurious == other.spurious
        return isequal

    def __add__(self, other: 'MatchCount'):
        """
        add two matching counts
        """
        if not isinstance(other, MatchCount):
            return NotImplemented
        correct = self.correct + other.correct
        incorrect = self.incorrect + other.incorrect
        partial = self.partial + other.partial
        missing = self.missing + other.missing
        spurious = self.spurious + other.spurious
        return MatchCount(correct=correct, incorrect=incorrect, partial=partial, missing=missing, spurious=spurious)

    def sum(self, gold: bool = True) -> int:
        """
        sum the relevant counts together
        :param gold: if the dataset is gold set
        :type gold: bool
        :return: ACT
        :rtype:
        """
        if gold:
            return self.correct + self.incorrect + self.missing + self.partial
        else:
            return self.correct + self.incorrect + self.spurious + self.partial

    def get_count(self) -> Tuple[int,int,int,int,int]:
        return self.correct, self.incorrect, self.partial, self.missing, self.spurious

    def __str__(self):
        return f"MatchCount: correct={self.correct}, incorrect={self.incorrect}, partial={self.partial}, " \
            f"missing={self.missing}, spurious={self.spurious}"


def has_overlap(gold: Entity, response: Entity) -> bool:
    """
    check whether the gold entity and the response entity overlap
    :param gold: gold entity
    :type gold: Entity
    :param response: response entity
    :type response: Entity
    :return: overlaps or not
    :rtype: bool
    """
    return gold.span[0] < response.span[1] and response.span[0] < gold.span[1]


def validate_label_seq(label_seq: List[str], ground_data: List[str] = None) -> bool:
    """
    Validate the label sequence of a sentence
    An invalid label sequence would be ['O', 'I-GP'] because an entity should start with 'B-'
    :param label_seq: a list of actual label sequence of a sentence
    :type label_seq: List[str]
    :param ground_data: tokens of a sentence
    :type ground_data: tokens of a sentence
    :return: True for valid label sequence
    :rtype: bool
    """
    # prohibited label sequence: 'O' -> 'I'
    prev_pos, prev_tag = ('O', 'O')
    for label in label_seq:
        if label == 'O':
            pos, tag = ('O', 'O')
        else:
            pos, tag = label.split('-')
            if pos not in ('B', 'I'):
                logging.warning(f"expect label starts with B or I but got: {label}")
                return False
        if pos == 'I':
            if prev_pos == 'O':
                logging.warning(f"invalid label sequence, I comes after O: {list(zip(label_seq, ground_data)) if ground_data else label_seq}")
                return False
            if prev_pos in ('B', 'I') and prev_tag != tag:
                logging.warning(f"invalid label sequence, tag inconsistent: {list(zip(label_seq, ground_data)) if ground_data else label_seq}")
                return False
        prev_pos, prev_tag = pos, tag
    return True


def extract_entity(seq: List[str], *args) -> List[Entity]:
    """
    extract entity from label sequence
    :param seq: a list of labels in a sentence
    :type seq: List[str
    :return: A list of entity object
    :rtype: List[Entity]
    """
    entities = []
    tmp = []

    for i, token in enumerate(seq):
        if token == 'O':
            pos, tag = 'O', 'O'
        else:
            pos, tag = token.split('-')
        label = Entity_Label(index=i, pos=pos, tag=tag)

        if pos == 'B' or pos == 'O':
            if tmp:
                entities.append(Entity(span=(tmp[0].index, i), tag=tmp[0].tag))
                tmp[:] = []
            if pos == 'B':
                tmp.append(label)
        elif pos == 'I':
            tmp.append(label)
    if tmp:
        entities.append(Entity(span=(tmp[0].index, tmp[-1].index+1), tag=tmp[0].tag))
    return entities


def agreement_sentence(entities_gold: List[Entity], entities_response: List[Entity]) -> \
        Tuple[MatchCount, MatchCount, MatchCount, MatchCount]:
    """
    calculate the correct, partial, missing and spurious entities between gold and response entities
    :param entities_gold: A list of entities from gold labels of a sentence
    :type entities_gold: List[Entity]
    :param entities_response: A list of entities from response labels of a sentence
    :type entities_response: List[Entity]
    :return: A tuple of match counts: [correct_total, partial_total, missing_total, incorrect_total, spurious_total]
    :rtype: Tuple[int, int, int, int, int]
    """
    strict = MatchCount()
    exact_boundary = MatchCount()
    partial_boundary = MatchCount()
    type_matching = MatchCount()

    missing_count_gold = [True for _ in range(len(entities_gold))]
    spurious_count_resp = [True for _ in range(len(entities_response))]

    for i, annoA in enumerate(entities_gold):
        for j, annoB in enumerate(entities_response):
            if has_overlap(annoA, annoB):
                missing_count_gold[i] = False
                spurious_count_resp[j] = False

                # type matching: check overlap and type
                if annoA.tag == annoB.tag:
                    type_matching.correct += 1
                else:
                    type_matching.incorrect += 1

                if annoA.span == annoB.span:
                    # boundary match: check exact boundary
                    exact_boundary.correct += 1
                    partial_boundary.correct += 1
                    # strict match: boundary ok and check type
                    if annoA.tag == annoB.tag:
                        strict.correct += 1
                    else:
                        strict.incorrect += 1
                else:
                    # strict: boundary not exact match
                    strict.incorrect += 1
                    # exact boundary match: boundary not exact match
                    exact_boundary.incorrect += 1
                    # partial match: partial match
                    partial_boundary.partial += 1

    missing = sum(missing_count_gold)
    spurious = sum(spurious_count_resp)

    strict.missing, exact_boundary.missing, partial_boundary.missing, type_matching.missing = [missing]*4
    strict.spurious, exact_boundary.spurious, partial_boundary.spurious, type_matching.spurious = [spurious]*4

    return strict, exact_boundary, partial_boundary, type_matching


def agreement_dataset(gold: List[List[str]], response: List[List[str]],
                      validate_label: bool = True, X: List[List[str]] = None) -> Tuple[List[MatchCount], int, int]:
    """
    clacuate the agreement between gold set and response set
    :param gold: A list of label sequence of sentences from gold set
    :type gold: List[List[str]]
    :param response: A list of label sequence of sentences from response set
    :type response: List[List[str]]
    :param validate_label: if True, validate the label sequence
    :type validate_label: bool
    :param x: A list of text sequences
    :type X: List[List[str]]
    :return: A tuple of match counts and total counts:
    [correct_total, partial_total, missing_total, incorrect_total, spurious_total], gold_total, resp_total
    :rtype: Tuple[List[MatchCount], int, int]
    """
    assert len(gold) == len(response), f"expect {len(gold)} sentences but got {len(response)} sentences " \
       f"in response dataset"
    dataset_agreement = [MatchCount()]*4
    gold_ent_count = 0
    resp_ent_count = 0
    for i, label_seq_gold in enumerate(gold):
        if validate_label:
            if X:
                ground_data = X[i]
            else:
                ground_data = None
            assert validate_label_seq(label_seq_gold, ground_data), f"sent {i}: invalid gold label sequence\n"
            try:
                validate_label_seq(response[i], ground_data)
            except:
                logging.error(f"Could not validate label sequence between predictions and ground truth")

        entities_gold = extract_entity(label_seq_gold, i, 'gold')
        entities_resp = extract_entity(response[i], i, 'response')

        gold_ent_count += len(entities_gold)
        resp_ent_count += len(entities_resp)

        sent_agreement = agreement_sentence(entities_gold, entities_resp)
        dataset_agreement = list(map(add, dataset_agreement, sent_agreement))

    return dataset_agreement, gold_ent_count, resp_ent_count


def evaluate(agreement: MatchCount, beta: float = 1.0) -> Tuple[float, float, float]:
    """
    calculate the precision, recall and f1 score based on agreement
    :param agreement: A tuple of match counts:
    [correct_total, partial_total, missing_total, incorrect_total, spurious_total]
    :type agreement: Tuple[int, int, int, int, int]
    :param beta: beta is chosen such that recall is considered beta times as important as precision
    :type beta: float
    :return: precision, recall, f1 score
    :rtype: Tuple[float, float, float]
    """
    p = precision_score(correct=agreement.correct,
                        incorrect=agreement.incorrect,
                        partial=agreement.partial,
                        spurious=agreement.spurious)
    r = recall_score(correct=agreement.correct,
                     incorrect=agreement.incorrect,
                     partial=agreement.partial,
                     missing=agreement.missing)
    f1 = f1_score(precision=p, recall=r, beta=beta)
    return p, r, f1


def semeval_scores(gold: List[List[str]], response: List[List[str]], digits: int = 3,
                   validate_label: bool = True, X: List[List[str]] = None) -> Dict[str, List]:
    """
    calculate the precision, recall and f1 score based on agreement
    :param gold: A list of label sequence of sentences from gold set
    :type gold: List[List[str]]
    :param response: A list of label sequence of sentences from response set
    :type response: List[List[str]]
    :param digits: Number of digits for formatting output floating point values
    :type digits: int
    :param validate_label: if True, validate the label sequence
    :type validate_label: bool
    :param X: A list of text sequences
    :type X: List[List[str]]
    :return: precision, recall, f1 score
    :rtype: Tuple[float, float, float]
    """
    match_counts = agreement_dataset(gold=gold, response=response, validate_label=validate_label, X=X)
    scores = {}
    for name, agree in zip(('strict', 'exact', 'partial', 'type'), match_counts):
        p, r, f1 = evaluate(agree)
        scores[name] = [round(p, digits), round(r, digits), round(f1, digits)]
    return scores


def semeval_scores_report(gold: List[List[str]], response: List[List[str]], digits: int = 2,
                          validate_label: bool = True, X: List[List[str]] = None) -> str:
    """
    calculate the precision, recall and f1 score based on agreement and generate a report
    :param gold: A list of label sequence of sentences from gold set
    :type gold: List[List[str]]
    :param response: A list of label sequence of sentences from response set
    :type response: List[List[str]]
    :param digits: Number of digits for formatting output floating point values
    :type digits: int
    :param validate_label: if True, validate the label sequence
    :type validate_label: bool
    :param X: A list of text sequences
    :type X: List[List[str]]
    :return: formatted report
    :rtype: str
    """
    # get the matches and agreements between the ground truth/gold dataset and
    # the predicted or manually created annotations
    match_counts, gold_ent_count, resp_ent_count = agreement_dataset(gold=gold, response=response,
                                                                     validate_label=validate_label, X=X)
    HEADERS = ('strict', 'exact', 'partial', 'type')
    SEMEVAL_NAMES = ('correct', 'incorrect', 'partial', 'missing', 'spurious')

    # get the counts for the different agreement outcomes across all annotations
    strict_counts, exact_counts, partial_counts, type_counts = (count.get_count() for count in match_counts)
    strict_scores, exact_scores, partial_scores, type_scores = (evaluate(agreement) for agreement in match_counts)
    rows = zip(SEMEVAL_NAMES, strict_counts, exact_counts, partial_counts, type_counts)
    longest_last_line_heading = 'Gold Total'
    name_width = max(len(cn) for cn in SEMEVAL_NAMES)
    width = max(name_width, len(longest_last_line_heading), digits)
    head_fmt = '{:>{width}s} ' + ' {:>9}' * len(HEADERS)

    # create rows and columns to write the report
    report = head_fmt.format('', *HEADERS, width=width)
    report += '\n\n'
    row_fmt_score = '{:>{width}s} ' + ' {:>9.{digits}f}' * 4 + '\n'
    row_fmt_count = '{:>{width}s} ' + ' {:>9,d}' * 4 + '\n'
    row_fmt_ent = '{:>{width}s} ' + ' {:>9,d}' + '\n'

    # add the results into the report
    row_str_len = 0
    for row in rows:
        report += row_fmt_count.format(*row, width=width)
        row_str_len = len(row_fmt_count.format(*row, width=width))
    report += '='*row_str_len + '\n'
    rows = zip(('precision', 'recall', 'f1 score'), strict_scores, exact_scores, partial_scores, type_scores)
    for row in rows:
        report += row_fmt_score.format(*row, width=width, digits=digits)
    report += '='*row_str_len + '\n'
    rows = (('Gold Total', gold_ent_count), ('Resp Total', resp_ent_count))
    for row in rows:
        report += row_fmt_ent.format(*row, width=width)
    report += '\n'

    return report


def precision_score(correct: int, incorrect: int, partial: int, spurious: int) -> float:
    """
    the denominator is the total number of entities produced by the system
    the equation used:
    ACT = COR + INC + PAR + SPU = TP + FP
    P = COR/ACT = TP/(TP+FP)
    if partial match allowed:
    P = (COR + 0.5*PAR)/ACT

    :param correct: number of gold entities exactly matched by response
    :type correct: int
    :param incorrect: number of gold entities wrongly annotated (wrong type) by response
    :type incorrect: int
    :param partial: number of gold entities partially annotated (same type and overlaps) by response
    :type partial: int
    :param spurious: number of response entities not in the gold entities
    :type spurious: int
    :return: precision score
    :rtype: float
    """
    numerator = correct + 0.5*partial
    # A easier way to calculate denominator is by counting number of entities in response
    # thus we dont need to count missing, incorrect and spurious
    denominator = correct + incorrect + partial + spurious
    try:
        precision  = numerator/denominator
    except ZeroDivisionError:
        logging.error(f"Could not determine precision score")
        precision = 0
        pass
    return precision


def recall_score(correct: int, incorrect: int, partial: int, missing: int) -> float:
    """
    the denominator is the total number of entities in the gold data
    the equation used:

    POS = COR + INC + PAR + MIS = TP + FN
    R = COR/POS = TP/(TP+FN)
    if partial match allowed:
    R = (COR + 0.5*PAR)/POS

    :param correct: number of gold entities exactly matched by response
    :type correct: int
    :param incorrect: number of gold entities wrongly annotated (wrong type) by response
    :type incorrect: int
    :param partial: number of gold entities partially annotated (same type and overlaps) by response
    :type partial: int
    :param missing: number of gold entities not in the response entities
    :type missing: int
    :return: recall score
    :rtype: int
    """
    numerator = correct + 0.5*partial
    # A easier way to calculate denominator is by counting number of entities in gold
    # thus we dont need to count missing, incorrect and spurious
    denominator = correct + incorrect + partial + missing
    try:
        recall = numerator/denominator
    except ZeroDivisionError:
        logging.error(f"Could not determine recall score")
        recall = 0
        pass

    return recall


def f1_score(precision: float, recall: float, beta: float = 1.0) -> float:
    """
    calculate f1 score given precision and recall score
    the equation used (beta f1 score):

    F1 = (1+ beta**2) * (precision*recall) / ((beta**2)*precision + recall)
    where beta is chosen such taht recall is considered beta times as important as precision

    if beta = 1:
    F1 = 2*precision*recall/(precision+recall)

    :param precision: precision score
    :type precision: float
    :param recall: recall score
    :type recall: float
    :param beta: beta is chosen such that recall is considered beta times as important as precision,
    :type beta: float
    :return: f1 score
    :rtype: float
    """
    numerator = (beta**2 + 1)*precision * recall
    denominator = (beta**2)*precision + recall
    try:
        f1 = numerator/denominator
    except ZeroDivisionError:
        logging.error(f"Could not determine F1 score")
        f1 = 0
        pass
    
    return f1


def load_IOBdataset(data_path: str, targets: List[str] = None) -> Tuple[List[List[str]], List[List[str]]]:
    """
    load the IOB dataset, which is in csv format
    :param data_path: path to the csv file of IOB dataset
    :type data_path: str
    :param targets: a list of interest types
    :type targets: List[str]
    :return: list of labels of every sentence in dataset
    :rtype: List[List[str
    """
    # nested empty list to write the lists of individual word tokens for each 
    # sentence from an IOB file to
    X = []
    # nested empty list to write the lists of individual labels for each 
    # sentence from an IOB file to
    y = []

    # empty list to append the word tokens to; this list will then be appended
    # to the global list "X" above
    X_sent = []
    # # empty list to append the labels to; this list will then be appended
    # to the global list "y" above
    y_sent = []

    # load the IOB 
    with open(data_path, 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        # each line is a token for a word in a sentence
        # a break between sentences is indicated by an empty line with no token and no tag
        for line in csv_reader:
            if line:
                # retrieve the 
                token, tag = line[0], line[-1]                
                X_sent.append(token)
                if targets:
                    if tag.split('-')[-1] in set(targets):
                        y_sent.append(tag)
                    else:
                        y_sent.append('O')
                else:
                    y_sent.append(tag)
            else:
                # we reach the end of a sentence; append to the global list
                if len(X_sent) > 0:
                    X.append(X_sent)
                    y.append(y_sent)
                X_sent = []
                y_sent = []

    # return the global, nested list of sentences with corresponding IOB labels
    return X, y


def semeval_report(gold_path: str, response_path: str, targets: List[str] = None,
                   digits: int = 2, validate_label: bool = True) -> str:
    """
    report semeval scores by providing file paths to gold and response datasets
    :param gold_path: path to gold dataset file
    :type gold_path: str
    :param response_path: path to response dataset file
    :type response_path: str
    :param targets: a list of interest types
    :type targets: List[str]
    :param digits: Number of digits for formatting output floating point values
    :type digits: int
    :param validate_label: if True, validate the label sequence
    :type validate_label: bool
    :return: semeval scores report
    :rtype: str
    """
    # open the ground truth data and reformat to have nested list for sentences
    # and tokens; and check the number of sentences in it
    gold_data, gold_labels = load_IOBdataset(gold_path, targets=targets)
    logging.info(f"Number of samples in ground truth data: {len(gold_data)}")
    logging.info(f"Number of ground truth labels: {len(gold_labels)}")

    # open the predicted/manually created data and reformat to have nested list
    # for sentences and tokens; and check the number of sentences in it
    resp_data, resp_labels = load_IOBdataset(response_path, targets=targets)
    logging.info(f"Number of samples in predicted data: {len(resp_data)}")
    logging.info(f"Number of predicted labels: {len(resp_labels)}")


    # flatten the gold data sentences to no longer be a list of strings
    flat_gold = [' '.join(sublist) for sublist in gold_data]
    # flatten the predicted/manually created data sentences to no longer be a
    # list of strings
    flat_resp = [' '.join(sublist) for sublist in resp_data]

    # create gold dataframe
    gold_df = pd.DataFrame(zip(flat_gold, gold_labels),
                           columns =['data', 'gold_labels'])
    # create predicted/manually created dataframe
    resp_df = pd.DataFrame(zip(flat_resp, resp_labels),
                           columns =['data', 'resp_labels'])

    # merge the two dataframes to get total length
    merged_df = pd.merge(gold_df, resp_df, on='data', how='outer')
    merged_df['data'] = merged_df['data'].apply(lambda x: x.split(" "))
    # get the number of tokens in each cell; i.e. each cell in column "data"
    # will hold a list of strings and each string represents a word token;
    # number of tokens is needed to later be able to generate the correct
    # number of labels when filling "NaN" values to match the number of
    # sentences in the ground truth/gold and the predicted/manually
    # created data
    merged_df['data_length'] = merged_df['data'].apply(lambda x: len(x))

    # define a NaN mask to find the number of rows that are only present
    # in one of the two merged dataframes and therefore appear as "NaN"
    # values in the new dataframe after merging
    nan_mask = pd.isnull(merged_df).any(axis=1)
    merged_na = merged_df[nan_mask]
    logging.info(f"Number of rows/sentences with NaN: {len(merged_na)}")

    # define two functions to run over the respective columns for ground truth/
    # gold standard as well as the predicted/manually created data; this is to
    # enter the correct number of labels into the respective label columns of
    # the merged dataframe
    def replace_gold_nan_with_O(row):
        if isinstance(row['gold_labels'], list):
            return row
        else:
            label_len = row['data_length']
            row['gold_labels'] = list('O' * int(label_len))
            return row

    def replace_resp_nan_with_O(row):
        if isinstance(row['resp_labels'], list):
            return row
        else:
            label_len = row['data_length']
            row['resp_labels'] = list('O' * int(label_len))
            return row
        
    # run over the ground truth/gold data column and replace "NaN" with "O"
    # to the same length as there are tokens in the sentence
    merged_df = merged_df.apply(replace_gold_nan_with_O, axis=1)

    # run over the predicted/manually created data column and replace "NaN"
    # with "O" to the same length as there are tokens in the sentence
    merged_df = merged_df.apply(replace_resp_nan_with_O, axis=1)

    # turn the columns "data", "gold_labels" and "resp_labels" into lists;
    # the "data" column will now be a nested list containing all the sentences
    # each of them split into a list of word tokens; the "gold_labels" column
    # will be turned into a nested list where each individual list contains
    # the labels for each word token in the sublists in "data"; each of the
    # corresponding sublists wil be of same length; the same applies to
    # "resp_labels"
    data = merged_df["data"].to_list()
    gold_labels = merged_df["gold_labels"].to_list()
    resp_labels = merged_df["resp_labels"].to_list()

    logging.info(f"Length of final ground truth labels: {len(gold_labels)}")
    logging.info(f"Length of final predicted labels: {len(resp_labels)}")
    
    # check whether label validation has been set
    if validate_label:
        X = data
    else:
        X = None

    # calculate and return the scores in a report
    return semeval_scores_report(gold=gold_labels, response=resp_labels, digits=digits,
                                 validate_label=validate_label, X=X)


