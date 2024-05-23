import pandas as pd
import json
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize
from collections import Counter
from nltk.util import ngrams

from sklearn.metrics import accuracy_score

def compare_overlap_list(answer_as, answer_bs, new_answers):
    overlap_rate = 0
    non_overlap_rate = 0
    unempty_num = 0
    global_overlap_count = 0
    non_overlap_answers = []
    for answer_a, answer_b, new_answers_sublist in zip(answer_as,answer_bs,new_answers):
        subnon_overlap_answers = []
        if answer_b !=[]:
            #answer_b = answer_b.split("\n")
            #answer_a = " ".join(answer_a)
            overlap_count = 0
            for word in answer_b:
                word = word.strip().lower()
                whole_word = word
                if " " in word:
                    word = word.split(" ")[0]
                if word in " ".join(answer_a).lower():
                #if word in " ".join(answer_a).lower():
                    overlap_count += 1
                else:
                    subnon_overlap_answers.append(whole_word)
            non_overlap_rate += (len(answer_b) - overlap_count) / len(new_answers_sublist)
            overlap_rate += overlap_count / len(answer_b)
            unempty_num+=1
        non_overlap_answers.append(subnon_overlap_answers)
        global_overlap_count += overlap_count

    # with open("../data/answers/llama2-7b/answer_1k//13-13b-mask/13-13b-mask-non-overlap_boundary_whole_answers.txt", "w",
    #           encoding="utf8") as f:
    #     for list in non_overlap_answers:
    #         if list == []:
    #             f.write("none" + "\n")
    #         else:
    #             f.write(" ".join(list).replace("\n", "") + "\n")

    overlap_rate = overlap_rate/unempty_num
    non_overlap_rate = non_overlap_rate/unempty_num
    overall_len = sum([len(i) for i in answer_bs])

    return global_overlap_count, overall_len, overlap_rate, non_overlap_rate

def find_near_duplicate_answers(list1):# list1 = ['pandas', 'Chinese tigers', 'Tiger']
    #return  list1
    lemmatizer = WordNetLemmatizer()

    # Define function to turn NLTK pos_tag to wordnet compatible PoS:
    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None
    # Iterate through your list:
    result_list = []

    for word in list1:
        res = word_tokenize(word)
        res = pos_tag(res)
        lemmatized_word = []
        for word, pos in res:
            wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
            lemmatized_word.append(lemmatizer.lemmatize(word.lower(), pos=wordnet_pos))
        result_list.append(" ".join(lemmatized_word))

    return  result_list

def select_new_answers_with_labels(existing_answers, new_answers, new_labels, predicted_labels):
    selected_new_answers = []
    selected_new_labels = []
    selected_predicted_labels = []
    selected_answers_ratio = 0
    #total_new_answers = sum([len(sub_list) for sub_list in new_labels])
    boundary_answer_num = 0
    unempty = 0
    for existing_sublist, new_sublist, new_sublist_labels, predicted_sublist_labels in zip(existing_answers,
                                                                                           new_answers, new_labels,
                                                                                           predicted_labels):
        selected_sublist = []
        selected_labels_sublist = []
        selected_predicted_labels_sublist = []
        # new_sublist = new_sublist[: len(new_sublist) // 10]
        # new_sublist_labels = new_sublist_labels[: len(new_sublist) // 10]
        # predicted_sublist_labels = predicted_sublist_labels[: len(new_sublist) // 10]
        flag = 0
        for str, label, predicted_label in zip(new_sublist, new_sublist_labels, predicted_sublist_labels):
            #if True:#str not in "".join(existing_sublist):
            if  (predicted_label==1 and label ==1) or (predicted_label == 2 and label != 2) or (predicted_label == 1 and label != 1) or (predicted_label == 0 and label != 0):
                if str not in "".join(existing_sublist):
                    selected_sublist.append(str)
                    selected_labels_sublist.append(label)
                    selected_predicted_labels_sublist.append(predicted_label)
                    boundary_answer_num+=1

                    if flag == 0:
                        unempty+=1
                    flag = 1


        selected_answers_ratio+= len(selected_sublist) / len(new_sublist)
        selected_new_answers.append(selected_sublist)
        selected_new_labels.append(selected_labels_sublist)
        selected_predicted_labels.append(selected_predicted_labels_sublist)

    selected_answers_count = sum([len(sub_list) for sub_list in selected_new_labels])
    selected_answers_ratio = selected_answers_ratio / unempty

    return selected_new_answers, selected_new_labels, selected_predicted_labels, selected_answers_ratio

print(root_path)
answer_col_name = 'answer_entities_3'
label_col_name = "3"
start_index = 0

with open(root_path + 'answers_100_evaled_full_labeled.json', 'r') as f:
    json_list = json.load(f)
with open("../data/answers/answers_0.9k_7b.1.json", "r") as f:
    existing_answers_json = json.load(f)

# gpt4_gt_path = '../data/answers/gpt-4/answers_1k.json'
# with open(gpt4_gt_path, "r") as f:
#     existing_answers_json = json.load(f)

existing_answers = []
new_answers = []
fact_list = []
label_list = []
final_data_list = []
count = 0

for index, row in excel_df.iterrows():
    # if index >10 :
    #     continue
    if 1 or row["q"] == 1:
        count+=1
        fact_temp = [int(each.replace(".","")) for each in row[label_col_name].strip().split()]
        for dict in json_list:
            if dict['question'] == row['question']:
                label_temp = dict["verification labels"][start_index:]
                break


        if len(fact_temp) == len(label_temp):
            fact_list.append(fact_temp)
            label_list.append(label_temp)
            new_answers.append(find_near_duplicate_answers(row[answer_col_name].split("\n")))
            for dict in existing_answers_json:
                if dict['question'] == row['question']:
                    existing_answers.append(find_near_duplicate_answers(dict['answer_entities'].split("\n")))

all_selected_new_answers, selected_new_labels, selected_predicted_labels, selected_answers_ratio = select_new_answers_with_labels(
    existing_answers, new_answers, fact_list, label_list)

all_fact_labels = []
for each in selected_new_labels:
    all_fact_labels+=each


all_consistency_labels = []
for each in selected_predicted_labels:
    all_consistency_labels+=each

all_pred_labels = []
for each in label_list:
    all_pred_labels+=each

for i in range(len(all_consistency_labels)):
    if all_consistency_labels[i] == 1:
        if all_fact_labels[i] == 1:
            correct += 1
        else:
            incorrect += 1
bd_answer = 0

import numpy as np


def compute_label_statistics(list1, list2):
    if len(list1) != len(list2):
       raise ValueError("List1 and List2 must be of the same length")
    matrix = np.zeros((3, 3))  # 3x3 matrix
    for l1, l2 in zip(list1, list2):
        if l2 not in[0,1,2]:
            l2 = 0
        if l1 not in[0,1,2]:
            l1 = 0
        matrix[l1][l2] += 1
    percentage_matrix = matrix / np.sum(matrix)
    return percentage_matrix

percentage_matrix = compute_label_statistics(all_fact_labels,all_consistency_labels)
print(percentage_matrix)
exit()
overlap_count, overall_len, overlap_rate, non_overlap_rate = compare_overlap_list(existing_answers, all_selected_new_answers,new_answers)
