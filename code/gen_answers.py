import openai, time, json, re
import itertools
import os
import pickle

counter = 0
def format_answers(answers):
    all_matches = []
    for answer in answers:
        lines = answer.split("\n")
        matches = []
        for line in lines:
            match = re.search(r'\b\d+\.\s\"(.+?)\"', line)
            if match:
                matches.append(match.group(1))
            else:
                matches += [i[1] for i in re.findall(r'\b\d+\.\s(?:\"(.+?)\"|\s?(.+?))(?:\s\(.*\)|\s\u2013|-|:\s?|\n|$)', line)]

        all_matches+=matches
        #print(matches)
        #matches = re.findall(r'\b\d\.\s([\w\s\-]+)(?:\s\(.*\)|:)', answer)
        #matches += clean_keywords(answer)
        #matches += re.findall(r'(\d+\.\s(.*?)(?:\s–|:|\n| \())|"(.*)"', answer)
        #matches += re.findall(r'\b\d+\.\s(.+?)(?:\s\(.*\)|\s\u2013|-|:\s?|\n)', answer)
        #print(matches)
    return all_matches
# answers = [
#      """
# 1. "2001: A Space Odyssey" (1968)
# 2. "Blade Runner" (1982)
# 3. "War Games" (1983)
# 4. "Short Circuit" (1986)
# 5. "RoboCop" (1987)
# 6. "Terminator 2: Judgment Day" (1991)
# 7. "Ghost in the Shell" (1995)
# 8. "The Matrix" (1999)
# 9. "Bicentennial Man" (1999)
# 10. "Metropolis" (1927)
# 11. "Colossus: The Forbin Project" (1970)
# 12. "Tron" (1982)
# 13. "Runaway" (1984)
# 14. "D.A.R.Y.L." (1985)
# 15. "Electric Dreams" (1984)
# 16. "Short Circuit 2" (1988)
# 17. "Demon Seed" (1977)
# 18. "The Stepford Wives" (1975)
# 19. "Westworld" (1973)
# 20. "Slaughterhouse-Five" (1972)
#
# ----------------------------------
#
# 1. "A.I. Artificial Intelligence" (2001)
# 2. "The Terminator" (1984)
# 3. "Total Recall" (1990)
# 4. "The Lawnmower Man" (1992)
# 5. "Star Trek: First Contact" (1996)
# 6. "Dark City" (1998)
# 7. "eXistenZ" (1999)
# 8. "Virtuosity" (1995)
# 9. "Universal Soldier" (1992)
# 10. "Screamers" (1995)
# 11. "Cherry 2000" (1987)
# 12. "Wired" (1989)
# 13. "Johnny Mnemonic" (1995)
# 14. "Brainscan" (1994)
# 15. "The Thirteenth Floor" (1999)
# 16. "Azureus Rising" (1997)
# 17. "The City of Lost Children" (1995)
# 18. "Arcade" (1993)
# 19. "Hollow Man" (2000)
# 20. "The Iron Giant" (1999)
#
# ----------------------------------
#
# 1. "Moontrap" (1989)
# 2. "Solo" (1996)
# 3. "Making Mr. Right" (1987)
# 4. "Hardware" (1990)
# 5. "Nemesis" (1992)
# 6. "Death Machine" (1994)
# 7. "Robot Jox" (1989)
# 8. "Cyborg 2" (1993)
# 9. "The Bride" (1985)
# 10. "A.P.E.X." (1994)
# 11. "Project Shadowchaser III" (1995)
# 12. "Tetsuo: The Iron Man" (1989)
# 13. "Prototype" (1983)
# 14. "Galaxy Express 999" (1979)
# 15. "The Black Hole" (1979)
# 16. "The Day the Earth Stood Still" (1951)
# 17. "Saturn 3" (1980)
# 18. "Futureworld" (1976)
# 19. "Android" (1982)
# 20. "Robo Warriors" (1996).
#     """
# ]
# print(format_answers(answers))
# exit()
def generate(message, rounds):
    generations = []
    openai.api_key = ""
    openai.api_base = ""
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
    ask4more = message.replace("a list of", "more")
    for i in range(rounds):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=1.5,
            #model="gpt-3.5-turbo",
            messages=messages
        )
        messages.append({'role':'system','content':response['choices'][0]['message']['content']})
        messages.append({'role':'user','content':ask4more})
        generations.append(response['choices'][0]['message']['content'])
    return generations


# if os.path.isfile('../data/answers/save_state/save_state.pkl'):
#     with open('../data/answers/save_state/save_state.pkl', 'rb') as f:
#         list_answers, counter = pickle.load(f)
# else:
#     list_answers = []
#     counter = 0
def gen_answer():
    with open('../data/answers/answers_0.9k_7b.1.json', 'r') as f:
        questions_list = json.load(f)

    if not os.path.exists('../data/answers/save_state'):
        os.mkdir('../data/answers/save_state')

    def exception_handler(func):
        global counter

        def wrapper(*args, **kwargs):
            global counter

            if counter % 10 == 0:  
                print(counter)
                with open('../data/answers/save_state/save_state.pkl', 'wb') as f:
                    pickle.dump((list_answers, counter), f)
                with open('../data/answers/answers_temp.json', 'w') as f:
                    json.dump(list_answers, f)
            counter += 1
            try:
                return func(*args, **kwargs)
            except Exception:
                print("0 ", counter)
                return None

        return wrapper

    @exception_handler
    def extend_question_dict(question_dict):
        question = question_dict["question"]
        answer = generate(question, rounds=1)  #
        question_dict["answer"] = answer  # 
        question_dict["answer_entities"] = format_answers(answer)  #
        return question_dict

    if os.path.isfile('../data/answers/save_state/save_state.pkl'):
        with open('../data/answers/save_state/save_state.pkl', 'rb') as f:
            list_answers, counter = pickle.load(f)
    else:
        list_answers = []
        counter = 0

    for question_dict in questions_list[counter:]:
        new_question_dict = {'question':question_dict['question']}
        new_question_dict = extend_question_dict(new_question_dict)
        if new_question_dict is not None:
            list_answers.append(new_question_dict)
        if counter == 3:
            break

    with open('../data/answers/answers.json', 'w') as f:
        json.dump(list_answers, f)

def gen_left_answer():
    full_answer_list = []
    with open('../data/answers/answers_0.9k_7b.1.json', 'r') as f:
        questions_list = json.load(f)
    with open('../data/answers/answers.json', 'r') as f:
        answers_list = json.load(f)
    i = 0
    count = 0
    for item in questions_list:
        if item['question'] == answers_list[i]['question']:
            temp_dict = answers_list[i]
            temp_dict["answer_entities"] = format_answers(temp_dict["answer"])
            full_answer_list.append(temp_dict)
            i+=1
        else:
            count+=1
            print(count)
            question = item['question']
            answer = generate(question, rounds=3) 
            item["answer"] = answer  
            item["answer_entities"] = format_answers(answer)
            full_answer_list.append(item)
    print(len(answers_list))
    print(len(questions_list))
    print(len(full_answer_list))
    with open('../data/answers/full_answers.json', 'w') as f:
        json.dump(full_answer_list, f)

gen_answer()