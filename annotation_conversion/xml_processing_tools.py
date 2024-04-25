# importing necessary modules/libraries
from bs4 import BeautifulSoup
import en_core_sci_sm
import pandas as pd
import math
import random
import pathlib
import csv
from nltk.tokenize import WordPunctTokenizer, wordpunct_tokenize
from tqdm import tqdm
import logging

def split_into_sentences(paragraph, paragraph_start):
    """
    Splitting text blocks like paragraphs into individual sentences and create a
    nested list to be returned; each sub-list has the following elements:
    [sent, start_char, end_char] 

    Input

    :param paragraph: block of text in a continuous string
    :type paragraph: str

    :param paragraph_start: paragraph offset
    :type paragraph_start: int

    
    Output

    :return: sentences_to_return; paragraph as a nested list of lists; each
             sub-list corresponds to a sentences and has the followig format:
             [sent, start_char, end_char] 
    :rtype: list[list[]]
    """
    # using normal spacy
    # loading spacy and english scientific vocab
    nlp = en_core_sci_sm.load()
    # passing the raw text for a paragraph
    doc = nlp(paragraph)

    # setting the paragraph start; this variable will be update with every new paragraph
    # processed to ensure the correct starting offset for a specific paragraph is used
    initial = paragraph_start
    
    # defining an empty list to append the next offset value to after sentence splitting;
    # this is needed as the initial offset is for the paragraph only and not for
    # individual sentences within the paragraph; this gets updated for each sentence that
    # is processed
    next_offset = []
    
    # appending the offset list with the initial offset value for the paragraph start
    next_offset.append(initial)
    
    # making an empty list to add individual sentences from paragraph to
    sentences_to_return = []
    
    # iterate over the individual sentences in the paragraph as split by SciSpacy
    for sent_ in doc.sents:
        # replace "new line" break with a white space
        sent = str(sent_).replace("\n", " ")
        
        # get the length of the current sentence to determine the position of the
        # stop character
        sent_length = len(sent)
        
        # because of above constraint on how the text is parsed, offset values need to be
        # adjusted to reflect what is found in the BioC XML file for each paragraph
        # this in turn means that the character/sentence start and end positions need adjusting
        # getting the last value from offset list which provides the starting point
        # for the current sentence
        last_in_list = next_offset[-1]
        start_char = last_in_list
        # setting the character end position as the sum of the starting position and the
        # length of the sentence that is currently be processed
        end_char = last_in_list + sent_length
        # assemble the sentence for appending
        sentence = [sent, start_char, end_char]
        # appending sentence to list for returning
        sentences_to_return.append(sentence)
        
        # update the offset list by using the sum from previous offset value and sentence length;
        # this provides the starting offset for the next sentence by additionally adding 1
        # and then appending offset list
        updated = end_char + 1
        # update the offset list by appending the latest offset value
        next_offset.append(updated)
        
    return sentences_to_return


def get_text_annos_from_xml(xml_in):
    """
    Finding the annotations in a BioC formatted XML files; annotations have
    either been created by using an autoannotator making entity type predictions
    or by a human annotator using the manual annitation tool TeamTat 

    Input

    :param xml_in: full path to BioC formatted XML file with annotations
    :type xml_in: str

    
    Output

    :return: flat_list; list of sentences for which annotations are found in
             'anno_list'; total length of list matches that of 'anno_list'
    :rtype: list[]

    :return: anno_list; a nested list of dictionaries; each dictionary contains
             the details for one annnotation with the following keys:
             'anno_id', 'anno_start', 'anno_end', 'anno_text', 'anno_type';
             total length dictionary list matches that of sentence list 'flat_list'
    :rtype: list[dict{}]

    """
    # loading and opening input BioC XML file holding raw text split by paragraphs 
    # with in-line annotations for each paragraph; tag <passage> ... </passage> surrounds
    # the paragraph and the in-line annotations as one block; within the block 
    # tag <annotation> ... </annotation> encloses each individual annotation for each paragraph

    # Reading the data inside the xml
    # file to a variable under the name
    # data
    with open(xml_in) as x:
        x_data = x.read()

    # Passing the stored data inside the beautifulsoup parser, storing the returned object
    Bs_data = BeautifulSoup(x_data, "xml")

    # getting the offsets for the different passages and storing them in a list
    offset_list = [int(passage.find("offset").text) for passage in Bs_data.find_all("passage")]

    # getting the length of each passage by counting the characters in the passage text string
    # and storing it in a list
    para_length_list = []
    for passage in Bs_data.find_all("passage"):
        try:
            if passage.find("text").text is not None:
                para_length = len(passage.find("text").text)
                para_length_list.append(para_length)
        except:
            logging.info(f"Could not get paragraph length")
        continue

    # print the number of annotations found in the BioC XML file
    xml_anno_list = [a for a in Bs_data.find_all("annotation")]
    anno_len = len(xml_anno_list)
    logging.info(f"Number of annotations found in BioC XML file for processing: {anno_len}")

    # the steps below of creating a dataframe and defining the start and end character positions was
    # necessary as there are gaps in the paragraph offset values picked from the BioC XML file;
    # this makes the character count across the document discontinuous;
    # also, as paragraphs are processed individually they all have a starting offset of "0" in
    # isolation, which doesn't match with what is recorded in BioC XML file

    # turning the offset list and the paragraph length list into a dataframe each
    df_offset_start = pd.DataFrame (offset_list, columns = ['offset_start'])
    df_paragraph_length = pd.DataFrame (para_length_list, columns = ['paragraph_length'])

    # combining the two dataframes along the column axis ignoring the index
    df_start_end = pd.concat([df_offset_start, df_paragraph_length], axis = 1, ignore_index=True)

    # replacing potential NaN values in the combined dataframe with "0"
    df_start_end = df_start_end.fillna(0).astype(int)

    # adding column labels to the combined dataframe
    df_start_end.columns = ['offset_start', 'paragraph_length']

    # calculating the sum between the starting offset for a paragraph and the length of a paragraph;
    # the resulting sum is equal to the end position of the paragraph
    df_start_end["offset_end"] = df_start_end["offset_start"] + df_start_end["paragraph_length"]

    # create empty lists to append processed sentences and annotations to
    # list of sentences from BioC XML file
    text_list_from_XML = []
    # list of annotations from BioC XML file
    anno_list = []

    # iterate over all text passages/paragraphs in the current BioC XML file
    for passage in Bs_data.find_all("passage"):
        # get the offset for the paragraph as is found in the BioC XML file
        offset = int(passage.find("offset").text)
        
        # ensure that the offset in the BioC XML file and the one saved in the start_end dataframe
        # match and get the start and end values recorded in the dataframe
        row = df_start_end.loc[df_start_end['offset_start'] == offset]    
        # get the starting offset for the paragraph from dataframe
        paragraph_start = row["offset_start"].values

        try:
            if passage.find("text").text is not None:
                # get the raw text of the current passage/paragraph
                paragraph = passage.find("text").text
                # send the current raw passage/paragraph text through the sentence splitter;
                # this will return a list of sentences from splitting the paragraph; all offsets
                # will be consistent and continuous for this specific paragraph as well as for the
                # entire document

                text_snippet = split_into_sentences(paragraph, paragraph_start[0])
                # append the returned list of processed sentences with correct start and end characters
                # for each sentence
                text_list_from_XML.append(text_snippet)

                # Finding all instances of tag "annotation" within a passage/paragraph
                passage_annotations = passage.find_all("annotation")
                
                # iterate over the returned list of annotations and extract details for each
                # annotation to be collected in a dictionary
                for annotation in passage_annotations:
                    # get the unique annotations ID
                    anno_id = annotation.get("id")
                    # get the location of the annotation which allows to determine
                    # a start and end character for the annotation
                    anno_loc = annotation.find("location")
                    # get the start character position for the annotation
                    begin_loc = int(anno_loc.get("offset"))
                    # get the length of the annotation
                    anno_length = int(anno_loc.get("length"))
                    # determine the end of the annotation by using the start and the length
                    anno_end = begin_loc + anno_length
                    # get the text span that is covered by the annotation stretch
                    anno_text = annotation.find("text").text
                    # get the annotation type
                    anno_type = annotation.find("infon", {"key" : "type"}).text
                    # create the dictionary for a given annotation
                    anno_dict = {"anno_id" : anno_id,
                                "anno_start" : begin_loc,
                                "anno_end" : anno_end,
                                "anno_text" : anno_text,
                                "anno_type" : anno_type}
                    # append the dictionary to a list for later use
                    anno_list.append(anno_dict)
        except:
            logging.info(f"Could not get passage text")
        continue
        

    # flatten the list of sentences as it currently is a list of lists;
    # each sentence will now be an element of the list
    flat_list = [item for sublist in text_list_from_XML for item in sublist]

    return flat_list, anno_list

def get_text_annos_from_xml_for_selected_sections(xml_in, annotator):
    """
    Finding the annotations in a BioC formatted XML files; annotations have
    either been created by using an autoannotator making entity type predictions
    or by a human annotator using the manual annitation tool TeamTat; looking
    at specific publication sections using the XML tags 'TITLE', 'ABSTRACT',
    'INTRO', 'FIG', 'RESULTS', 'DISCUSS' and 'TABLE'; this is used in context
    of calculating performance stats using the SemEval procedure; using an
    annotator name to isolate the annotations produced by a specific annotator

    Input

    :param xml_in: full path to BioC formatted XML file with annotations
    :type xml_in: str

    :param annotator: name or identifier of a specific annotator to find
                      annotations for
    :type annotator: str

    
    Output

    :return: flat_list; list of sentences for which annotations are found in
             'anno_list'; total length of list matches that of 'anno_list'
    :rtype: list[]

    :return: anno_list; a nested list of dictionaries; each dictionary contains
             the details for one annnotation with the following keys:
             'anno_id', 'anno_start', 'anno_end', 'anno_text', 'anno_type';
             total length dictionary list matches that of sentence list 'flat_list'
    :rtype: list[dict{}]

    """
    # loading and opening input BioC XML file holding raw text split by paragraphs 
    # with in-line annotations for each paragraph; tag <passage> ... </passage> surrounds
    # the paragraph and the in-line annotations as one block; within the block 
    # tag <annotation> ... </annotation> encloses each individual annotation for each paragraph

    # Reading the data inside the xml
    # file to a variable under the name
    # data
    with open(xml_in) as x:
        x_data = x.read()

    # Passing the stored data inside the beautifulsoup parser, storing the returned object
    Bs_data = BeautifulSoup(x_data, "xml")

    # getting the offsets for the different passages and storing them in a list
    offset_list = [int(passage.find("offset").text) for passage in Bs_data.find_all("passage")]

    # getting the length of each passage by counting the characters in the passage text string
    # and storing it in a list
    para_length_list = []

    # selected sections from BioC XML
    section_list = ["TITLE", "ABSTRACT", "INTRO", "FIG", "RESULTS", "DISCUSS", "TABLE"]

    for passage in Bs_data.find_all("passage"):
        try:
            p_keys = passage.find_all("infon")
            for key in p_keys:
                if key["key"] == "section_type" and key.text in section_list:
                    if passage.find("text").text is not None:
                        para_length = len(passage.find("text").text)
                        para_length_list.append(para_length)
        except:
            logging.info(f"Could not get paragraph length")
        continue

    # print the number of annotations found in the BioC XML file
    xml_anno_list = [a for a in Bs_data.find_all("annotation")]
    anno_len = len(xml_anno_list)
    logging.info(f"Number of annotations found in BioC XML file for processing: {anno_len}")


    # the steps below of creating a dataframe and defining the start and end character positions was
    # necessary as there are gaps in the paragraph offset values picked from the BioC XML file;
    # this makes the character count across the document discontinuous;
    # also, as paragraphs are processed individually they all have a starting offset of "0" in
    # isolation, which doesn't match with what is recorded in BioC XML file

    # turning the offset list and the paragraph length list into a dataframe each
    df_offset_start = pd.DataFrame (offset_list, columns = ['offset_start'])
    df_paragraph_length = pd.DataFrame (para_length_list, columns = ['paragraph_length'])

    # combining the two dataframes along the column axis ignoring the index
    df_start_end = pd.concat([df_offset_start, df_paragraph_length], axis = 1, ignore_index=True)

    # replacing potential NaN values in the combined dataframe with "0"
    df_start_end = df_start_end.fillna(0).astype(int)

    # adding column labels to the combined dataframe
    df_start_end.columns = ['offset_start', 'paragraph_length']

    # calculating the sum between the starting offset for a paragraph and the length of a paragraph;
    # the resulting sum is equal to the end position of the paragraph
    df_start_end["offset_end"] = df_start_end["offset_start"] + df_start_end["paragraph_length"]

    # create empty lists to append processed sentences and annotations to
    # list of sentences from BioC XML file
    text_list_from_XML = []
    # list of annotations from BioC XML file
    anno_list = []
    annotator_anno_list = []

    # iterate over all text passages/paragraphs in the current BioC XML file
    for passage in Bs_data.find_all("passage"):
        try:
            p_keys = passage.find_all("infon")
            for key in p_keys:
                if key["key"] == "section_type" and key.text in section_list:
                    # s_key = key.text
                    # logging.info(f"Working on section {s_key}")

                    # get the offset for the paragraph as is found in the BioC XML file
                    offset = int(passage.find("offset").text)
                    
                    # ensure that the offset in the BioC XML file and the one saved in the start_end dataframe
                    # match and get the start and end values recorded in the dataframe
                    row = df_start_end.loc[df_start_end['offset_start'] == offset]    
                    # get the starting offset for the paragraph from dataframe
                    paragraph_start = row["offset_start"].values

                    try:
                        if passage.find("text").text is not None:
                            # get the raw text of the current passage/paragraph
                            paragraph = passage.find("text").text

                            # send the current raw passage/paragraph text through the sentence splitter;
                            # this will return a list of sentences from splitting the paragraph; all offsets
                            # will be consistent and continuous for this specific paragraph as well as for the
                            # entire document

                            text_snippet = split_into_sentences(paragraph, paragraph_start[0])
                            #text_snippet = split_into_sentences(paragraph_clean, paragraph_start[0], paragraph_end[0])
                            # append the returned list of processed sentences with correct start and end characters
                            # for each sentence
                            text_list_from_XML.append(text_snippet)

                            # Finding all instances of tag "annotation" within a passage/paragraph
                            passage_annotations = passage.find_all("annotation")
                            
                            # iterate over the returned list of annotations and extract details for each
                            # annotation to be collected in a dictionary
                            for annotation in passage_annotations:
                                anno_name = annotation.find("infon", {"key" : "annotator"}).text
                                if annotator == anno_name:
                                    # get the unique annotations ID
                                    anno_id = annotation.get("id")
                                    # get the location of the annotation which allows to determine
                                    # a start and end character for the annotation
                                    anno_loc = annotation.find("location")
                                    # get the start character position for the annotation
                                    begin_loc = int(anno_loc.get("offset"))
                                    # get the length of the annotation
                                    anno_length = int(anno_loc.get("length"))
                                    # determine the end of the annotation by using the start and the length
                                    anno_end = begin_loc + anno_length
                                    # get the text span that is covered by the annotation stretch
                                    anno_text = annotation.find("text").text
                                    # get the annotation type
                                    anno_type = annotation.find("infon", {"key" : "type"}).text
                                    # create the dictionary for a given annotation
                                    anno_dict = {"anno_id" : anno_id,
                                                "anno_start" : begin_loc,
                                                "anno_end" : anno_end,
                                                "anno_text" : anno_text,
                                                "anno_type" : anno_type}
                                    # append the dictionary to a list for later use
                                    annotator_anno_list.append(anno_dict)
                                else:
                                    # get the unique annotations ID
                                    anno_id = annotation.get("id")
                                    # get the location of the annotation which allows to determine
                                    # a start and end character for the annotation
                                    anno_loc = annotation.find("location")
                                    # get the start character position for the annotation
                                    begin_loc = int(anno_loc.get("offset"))
                                    # get the length of the annotation
                                    anno_length = int(anno_loc.get("length"))
                                    # determine the end of the annotation by using the start and the length
                                    anno_end = begin_loc + anno_length
                                    # get the text span that is covered by the annotation stretch
                                    anno_text = annotation.find("text").text
                                    # get the annotation type
                                    anno_type = annotation.find("infon", {"key" : "type"}).text
                                    # create the dictionary for a given annotation
                                    anno_dict = {"anno_id" : anno_id,
                                                "anno_start" : begin_loc,
                                                "anno_end" : anno_end,
                                                "anno_text" : anno_text,
                                                "anno_type" : anno_type}
                                    # append the dictionary to a list for later use
                                    anno_list.append(anno_dict)
                    except:
                        logging.info(f"Could not get passage text")
                    continue
        except:
            logging.info(f"Could not get paragraphs for sections")
        continue

    # flatten the list of sentences as it currently is a list of lists;
    # each sentence will now be an element of the list
    flat_list = [item for sublist in text_list_from_XML for item in sublist]

    if annotator != None:
        return flat_list, annotator_anno_list
    else:
        return flat_list, anno_list

def get_text_annos_from_xml_as_json(xml_in):
    """
    Finding the annotations in a BioC formatted XML files; annotations have
    either been created by using an autoannotator making entity type predictions
    or by a human annotator using the manual annitation tool TeamTat; also find
    document ID in form of unique PubMedCentral ID from XML tags to be able
    to create a JSON file

    Input

    :param xml_in: full path to BioC formatted XML file with annotations
    :type xml_in: str

    
    Output

    :return: flat_list; list of sentences for which annotations are found in
             'anno_list'; total length of list matches that of 'anno_list'
    :rtype: list[]

    :return: anno_list; a nested list of dictionaries; each dictionary contains
             the details for one annnotation with the following keys:
             'anno_id', 'anno_start', 'anno_end', 'anno_text', 'anno_type';
             total length dictionary list matches that of sentence list 'flat_list'
    :rtype: list[dict{}]

    :return: doc_id_ex; document ID in form of unique PubMedCentral ID
    :rtype: str
    """
    # loading and opening input BioC XML file holding raw text split by paragraphs 
    # with in-line annotations for each paragraph; tag <passage> ... </passage> surrounds
    # the paragraph and the in-line annotations as one block; within the block 
    # tag <annotation> ... </annotation> encloses each individual annotation for each paragraph

    # Reading the data inside the xml
    # file to a variable under the name
    # data
    with open(xml_in) as x:
        x_data = x.read()

    # Passing the stored data inside the beautifulsoup parser, storing the returned object
    Bs_data = BeautifulSoup(x_data, "xml")

    # get ID of current document
    doc_id = Bs_data.find("id").text

    # get document source
    doc_src = Bs_data.find("source").text

    doc_id_ex = doc_src + doc_id

    # getting the offsets for the different passages and storing them in a list
    offset_list = [int(passage.find("offset").text) for passage in Bs_data.find_all("passage")]

    # getting the length of each passage by counting the characters in the passage text string
    # and storing it in a list
    para_length_list = []
    for passage in Bs_data.find_all("passage"):
        try:
            if passage.find("text").text is not None:
                para_length = len(passage.find("text").text)
                para_length_list.append(para_length)
        except:
            logging.warning(f"Could not get paragraph length")
        continue

    # the steps below of creating a dataframe and defining the start and end character positions was
    # necessary as there are gaps in the paragraph offset values picked from the BioC XML file;
    # this makes the character count across the document discontinuous;
    # also, as paragraphs are processed individually they all have a starting offset of "0" in
    # isolation, which doesn't match with what is recorded in BioC XML file

    # turning the offset list and the paragraph length list into a dataframe each
    df_offset_start = pd.DataFrame (offset_list, columns = ['offset_start'])
    df_paragraph_length = pd.DataFrame (para_length_list, columns = ['paragraph_length'])

    # combining the two dataframes along the column axis ignoring the index
    df_start_end = pd.concat([df_offset_start, df_paragraph_length], axis = 1, ignore_index=True)

    # replacing potential NaN values in the combined dataframe with "0"
    df_start_end = df_start_end.fillna(0).astype(int)

    # adding column labels to the combined dataframe
    df_start_end.columns = ['offset_start', 'paragraph_length']

    # calculating the sum between the starting offset for a paragraph and the length of a paragraph;
    # the resulting sum is equal to the end position of the paragraph
    df_start_end["offset_end"] = df_start_end["offset_start"] + df_start_end["paragraph_length"]

    # create empty lists to append processed sentences and annotations to
    # list of sentences from BioC XML file
    text_list_from_XML = []
    # list of annotations from BioC XML file
    anno_list = []

    # iterate over all text passages/paragraphs in the current BioC XML file
    for passage in Bs_data.find_all("passage"):
        # get section type a passage belongs to

        p_keys = passage.find_all("infon")
        for key in p_keys:
            if key["key"] == "section_type":
                section = key.text

        # get the offset for the paragraph as is found in the BioC XML file
        offset = int(passage.find("offset").text)
        
        # ensure that the offset in the BioC XML file and the one saved in the start_end dataframe
        # match and get the start and end values recorded in the dataframe
        row = df_start_end.loc[df_start_end['offset_start'] == offset]    
        # get the starting offset for the paragraph from dataframe
        paragraph_start = row["offset_start"].values

        try:
            if passage.find("text").text is not None:
                # get the raw text of the current passage/paragraph
                paragraph = passage.find("text").text
                # send the current raw passage/paragraph text through the sentence splitter;
                # this will return a list of sentences from splitting the paragraph; all offsets
                # will be consistent and continuous for this specific paragraph as well as for the
                # entire document

                text_snippet = split_into_sentences(paragraph, paragraph_start[0])
                text_snippet_ex = []
                for s in text_snippet:
                    s.append(section)
                    text_snippet_ex.append(s)

                text_list_from_XML.append(text_snippet_ex)

                # Finding all instances of tag "annotation" within a passage/paragraph
                passage_annotations = passage.find_all("annotation")
                
                # iterate over the returned list of annotations and extract details for each
                # annotation to be collected in a dictionary
                for annotation in passage_annotations:
                    # get the unique annotations ID
                    anno_id = annotation.get("id")
                    # get the location of the annotation which allows to determine
                    # a start and end character for the annotation
                    anno_loc = annotation.find("location")
                    # get the start character position for the annotation
                    begin_loc = int(anno_loc.get("offset"))
                    # get the length of the annotation
                    anno_length = int(anno_loc.get("length"))
                    # determine the end of the annotation by using the start and the length
                    anno_end = begin_loc + anno_length
                    # get the text span that is covered by the annotation stretch
                    anno_text = annotation.find("text").text
                    # get the annotation type
                    anno_type = annotation.find("infon", {"key" : "type"}).text
                    # create the dictionary for a given annotation
                    anno_dict = {"anno_id" : anno_id,
                                "anno_start" : begin_loc,
                                "anno_end" : anno_end,
                                "anno_text" : anno_text,
                                "anno_type" : anno_type}
                    # append the dictionary to a list for later use
                    anno_list.append(anno_dict)
        except:
            logging.warning(f"Could not get passage text")
        continue
        

    # flatten the list of sentences as it currently is a list of lists;
    # each sentence will now be an element of the list
    flat_list = [item for sublist in text_list_from_XML for item in sublist]

    # print the number of annotations found in the BioC XML file
    anno_len = len(anno_list)
    logging.info(f"Number of annotations found in BioC XML file for processing: {anno_len}")
    return doc_id_ex, flat_list, anno_list


# create indexes for train, test and devel set to distribute the samples
def get_train_dev_test_indxs(total_num_annotations):
    """
    creating index lists to split the sentences and their annotations into
    train, dev and test fractions

    Input

    :param total_num_annotations: list of total nnumber of sentences to be split
    :type total_num_annotations: list[]

    
    Output

    :return: train_ids; list of indeces to be used as training set
    :rtype: list[]

    :return: devel_ids; list of indeces to be used as development set
    :rtype: list[]

    :return: test_ids; list of indeces to be used as testing set
    :rtype: list[]
    """
    # set fraction of training data to 70% of the total
    percentage = 0.70

    # get the total number of samples
    nLines = total_num_annotations
    # split off 70% as training set
    nTrain = int(nLines * percentage)
    # take half of the reminder and set it as validation set
    nValid = math.floor((nLines - nTrain)/2)
    # everything that's left will be the text set
    nTest = nLines - (nTrain + nValid)

    # shuffle the lines in the full set
    deck = list(range(0, nLines))
    random.seed(45) # This will be fixed for reproducibility
    random.shuffle(deck)

    # use the line count from the three subsets to chunck the
    # shuffled full list
    train_ids = deck[0:nTrain]
    devel_ids = deck[nTrain:nTrain+nValid]
    test_ids = deck[nTrain+nValid:nTrain+nValid+nTest]

    # return the subsets as lists of indices
    return train_ids, devel_ids, test_ids

# find sub spans
def find_sub_span(sub_span_range, full_spans_range):
    """
    return 'sub_span_range' if match is found in 'full_spans_range',
    i.e. if the annotation has been found in the sentence

    Input

    :param sub_span_range: tuple containing start and end character position
                           of an annotation
    :type sub_span_range: tuple()

    :param full_spans_range: tuple containing start and end character position
                             of the sentence containing the annotation
    :type full_spans_range: tuple()
    
    Output

    :return: sub_span_range; tuple containing the start and end character
             position of the annotation 
    :rtype: tuple()

    """
    # if a sub span is present in full span return it
    if sub_span_range[0] in range(full_spans_range[0],full_spans_range[1]):
        return sub_span_range

# actual conversion to IOB format
def convert2IOB(text_data, ner_tags):
    """
    converting the sentences and their annotations into IOB formatted data;
    updating entity type labels to reflect IOB standard

    Input

    :param text_data: sentence as continuous string
    :type text_data: str

    :param ner_tags: nested list of annotations for sentence
    :type ner_tags: list[list[]]
    
    
    Output

    :return: arr; array of word tokens with matching token label in IOB format
    :rtype: arr

    """
    # instanciate an NLTK tokenizer to break each sentence into individual word tokens
    tokenizer = WordPunctTokenizer()

    # create three lists to append the results from tokenization, the respective character
    # spans for the tokens and the relevant annotations to
    tokens = []
    ners = []
    spans = []

    # split the sentence into tokens
    split_text = tokenizer.tokenize(text_data)
    # get the covered character span for each token
    span_text = list(tokenizer.span_tokenize(text_data))
    # for each word token append 'O' (outside annotation);
    # length of "arr" will be the total number of tokens
    # that have been created for the given sentence
    arr = ['O'] * len(split_text)

    # iterate over all the annotations for this sentence
    # "ner_tags" holds a list of annotations from the sentence dictionary
    # that comes with the sentence text that represents the key;
    # each element of the "ner_tags" list is a list itself with the items
    # "starting character", "ending character", "covered word/text",
    # "entity type of the annotation" 
    for each_tag in ner_tags:
        # get the start and end character position for the annotation
        span_list = (int(each_tag[0]), int(each_tag[1]))
        # get the individual word/s of text snippet covered by the annotation
        token_list = wordpunct_tokenize(each_tag[2])
        # get the entity type for the annotation
        ner_list = wordpunct_tokenize(each_tag[3])

        # if after the split there are more tokens than entity type labels
        # increase the number of entries for the particular entity type\
        # label by the number of tokens
        if (len(token_list) > len(ner_list)):
            ner_list = len(token_list) * ner_list
        # for each element in the extended list modify the entity type name;
        # if the first entry refers to the start of the annotated word span,
        # i.e. the first token then the entity type label is extended by the
        # prefix "B-" (for begin of annotation), any token after that has
        # the extension "I-" added (for inside annotation) 
        for i in range(0, len(ner_list)):
            # The logic here is look for the first B-tag and then append I-tag next
            if (i == 0):
                ner_list[i] = 'B-' + ner_list[i]
            else:
                ner_list[i] = 'I-' + ner_list[i]

        # append to the corresponding lists for individual tokens from the annotated
        # text span ("tokens"), the corresponding start and end character positions
        # for each token ("spans") and the modified entity type label for each token
        # ("ners"); all those lists should be of same length and can be combined when
        # an entire sentence has been processed
        tokens.append(token_list)
        ners.append(ner_list)
        spans.append(span_list)

    # try a few tests to make sure the returned lists are same length
    assert len(spans) == len(ners)
    assert len(ners) == len(tokens)
    assert len(spans) == len(tokens)

    # combine the list of tokens for the tokenized sentence with the
    # list of start and end character positions for each token
    split_token_span_list = list(zip(split_text, span_text))
    # combine the list of annotation span start and end character
    # positions with the nested list of the prefix-extended
    # entity type labels
    span_ner_list = list(zip(spans, ners))

    # get sub spans from the full spans of the ner
    sub_spans =[]

    # iterate over the combined list of annotation span (characterised
    # by starting and end character position) and nested list of
    # prefix-extended entity type labels
    # in full range ner e.g., [144, 150, 'COVID-19', 'DISO']
    # iterate over the tokens of the tokenized sentence
    # find matches between the span from the tokenized sentence and
    # the span from token in the annotation
    for each_span_ner_list in span_ner_list:
        # look at each token from the annotation span
        count = 0
        # count is to keep track of the B, I, sub tags in the ner list
        for each_token in split_token_span_list:
            # print("current token:")
            # print(each_token)
            # look at each token from the tokenized sentence
            sub_spans_ = find_sub_span(each_token[1], each_span_ner_list[0])
            # print("checking sub_span_")
            # print(sub_spans_)
            # if the two spans agree combine them and attach them to list 
            # "sub_spans"
            try:
                if sub_spans_:
                    sub_spans.append([sub_spans_, each_span_ner_list[1][count]])
                    count = count+1
            except:
                # print("current token:")
                # print(each_token)
                # print("current sub_span_")
                # print(sub_spans_)
                continue
    # iterate over the combined list of annotation span (characterised
    # by starting and end character position) after creating an iterable
    # index for it; iterate over all the subspans with their prefix expanded
    # entity type labels
    for i, each_span_token in enumerate(split_token_span_list):
        for each_ner_span in sub_spans:
            if each_span_token[1] == each_ner_span[0]:
                arr[i] = ''.join(each_ner_span[1])

    return zip(split_text, arr)

def convert_to_IOB_format(dictionary_dataset, train_ids, devel_ids, test_ids, path):
    """
    Write IOB converted annotations to disk as three separate tab-separated
    TSV files for train, dev and test set

    Input

    :param dictionary_dataset: dictionary containing the sentences as keys and the
                               annotations as values
    :type dictionary_dataset: dict{}

    :param train_ids: list of indices to create the training set
    :type train_ids: list[]
    
    :param devel_ids: list of indices to create the development set
    :type devel_ids: list[]

    :param test_ids: list of indices to create the testing set
    :type test_ids: list[]

    :param path: full path to output location
    :type path: str

    
    Output

    :return: train.tsv; IOB formatted annotations and sentences
    :rtype: TSV file

    :return: dev.tsv; IOB formatted annotations and sentences
    :rtype: TSV file

    :return: test.tsv; IOB formatted annotations and sentences
    :rtype: TSV file

    """
    # make output directory if it doesn't exist
    pathlib.Path(path).mkdir(parents = True, exist_ok = True)
    
    # open writable file objects for train. test and dev set to write 
    with open(path + 'train.tsv', 'w', newline = '\n') as f1, open(
              path + 'dev.tsv', 'w', newline = '\n') as f2, open(
              path + 'test.tsv', 'w', newline = '\n') as f3:

        train_writer = csv.writer(f1, delimiter = '\t', lineterminator = '\n')
        dev_writer = csv.writer(f2, delimiter = '\t', lineterminator = '\n')
        test_writer = csv.writer(f3, delimiter = '\t', lineterminator = '\n')

        # start an iterator with "0" to fetch sample; gets updated after every
        # execution  
        iter = 0

        # iterate over the content of the text dictionary, with the sentence as key
        # and the list of corresponding annotations as value
        for key, values in tqdm(dictionary_dataset.items(), total = len(dictionary_dataset), desc = "Converting to train/dev/test IOB files..."):
            # ensure the sentence is a string and feed it with its associated
            # annotations into the conversion function
            text = str(key)
            tagged_tokens = convert2IOB(text, values)

            # check in which of the index lists the current iterator is found
            # and add the write the returned IOB labeled tokens to the
            # corresponding list; after each tokenized sentence write an empty row;
            # this is latter used when converting to transformer readable embeddings
            # by filling the empty rows with the pattern '#*#*#*#*#*#*#*#*'
            # write the three sets to disk in the output directory
            if iter in train_ids:
                for each_token in tagged_tokens:
                    train_writer.writerow(list(each_token))
                train_writer.writerow('')

            elif iter in devel_ids:
                for each_token in tagged_tokens:
                    dev_writer.writerow(list(each_token))
                dev_writer.writerow('')

            elif iter in test_ids:
                for each_token in tagged_tokens:
                    test_writer.writerow(list(each_token))
                test_writer.writerow('')
            
            iter = iter+1

def convert_all_to_IOB(dictionary_dataset, path):
    """
    Write IOB converted annotations to disk as three separate tab-separated
    TSV files for train, dev and test set

    Input

    :param dictionary_dataset: dictionary containing the sentences as keys and the
                               annotations as values
    :type dictionary_dataset: dict{}

    :param path: full path to output location
    :type path: str

    
    Output

    :return: all.tsv; IOB formatted annotations and sentences
    :rtype: TSV file

    """
    pathlib.Path(path).mkdir(parents = True, exist_ok = True)
    with open(path + 'all.tsv', 'w', newline = '\n') as f1:
        all_writer = csv.writer(f1, delimiter = '\t', lineterminator = '\n')
        for key, values in tqdm(dictionary_dataset.items(), total = len(dictionary_dataset), desc = "Converting to single IOB file..."):
            # ensure the sentence is a string and feed it with its associated
            # annotations into the conversion function
            text = str(key)
            # write all annotations into a single IOB file; empty rows are
            # indicating a new sentence start are filled with the pattern
            # '#*#*#*#*#*#*#*#*' for later usage
            tagged_tokens = convert2IOB(text, values)
            for each_token in tagged_tokens:
                all_writer.writerow(list(each_token))
            all_writer.writerow('')
