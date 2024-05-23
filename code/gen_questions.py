import openai, time, json
import pandas as pd
import itertools

def generate(message, rounds):
    generations = []
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
    for i in range(rounds):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            #model="gpt-3.5-turbo",
            messages=messages
        )
        messages.append({'role':'system','content':response['choices'][0]['message']['content']})
        messages.append({'role':'user','content':'Tell me more questions.'})
        generations.append(response['choices'][0]['message']['content'])
    return generations

# def generate_questions(sufix=''):

#     with open('../data/prompt.txt', 'r', encoding='utf8') as f:
#         prompt = f.read()
#
#     with open('../data/topics.txt', 'r', encoding='utf8') as f:
#         topics = f.readlines()
#     topics = [i.strip().lower() for i in topics]
#
#     try:
#         with open("../data/questions/questions_dict"+sufix+".json", 'r') as file:
#             answer_dict = json.load(file)
#         count = len([num for num in answer_dict.values() if num != -1])
#
#     except:
#         count = 0
#         answer_dict = {}
#
#     i = 0
#     if -1 not in answer_dict.values():
#         missing = False
#     else:
#         missing = True
#     while count < len(topics) or missing:
#         if i == 100:
#             i = 0
#         if str(i) in list(answer_dict.keys()):
#             if answer_dict[str(i)] != -1:
#                 i+=1
#                 continue
#         try:
#             full_prompt = prompt.replace('xxxxx', topics[i])
#             generations = generate(full_prompt, rounds=3)
#             #questions.append(generations)
#             answer_dict[topics[i]] = generations
#             i += 1
#             count += 1
#         except Exception as e:
#             print("ID:", i)
#             print(str(e))
#             answer_dict[topics[i]] = -1
#             time.sleep(20)
#         if count % 1 == 0:
#             print(count, "/", len(topics))
#             with open("../data/questions/questions_dict" + sufix + ".json", 'w') as json_file:
#                 json.dump(answer_dict, json_file)
#
#         if -1 not in answer_dict.values():
#             missing = False
#         else:
#             missing = True

def generate_questions(sufix=''):
    with open('../data/prompt.txt', 'r', encoding='utf8') as f:
        prompt = f.read()
    with open('../data/topics.txt', 'r', encoding='utf8') as f:
        topics = f.readlines()
    answer_dict = {}
    topics = [i.strip().lower() for i in topics]
    for index, topic in enumerate(topics):
        full_prompt = prompt.replace('xxxxx', topic)
        generations = generate(full_prompt, rounds=3)
        answer_dict[topic] = generations
        print(index, "/", len(topics))
    with open("../data/questions/questions_dict_3.json", 'w') as json_file:
        json.dump(answer_dict, json_file)

generate_questions(sufix='')