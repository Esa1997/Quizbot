# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet


import itertools
import random

mapped_slots = {}
question_count = 0
quiz_ans_slots = []

QUESTION_LIST = {
    "0": {
        "question": "Fill in the blank. We need _________________ to breathe.",
        "options": ["air", "water", "food", ""],
        "answer": "air",
        "hint": "Something that around us and transparent",
        "type": "MCQ"},
    "1": {
        "question": "Identify the following equipment.",
        "image": "https://5.imimg.com/data5/AZ/ZI/MM/SELLER-48457887/magnifying-glass-available-in-100mm-90mm-75mm-63mm-sizes--500x500.jpg",
        "answer": "magnifying glass",
        "hint": "Enlarge an image of an object.",
        "type": "IMG"},
    "2": {
        "question": "What happens when you put a glass of water in the freezer?",
        "answer": "Becomes ice",
        "hint": "The state of water changes",
        "type": "QN"},
    "3": {
        "question": "True or False? The human skeleton is made up of less than 100 bones.",
        "answer": False,
        "hint": "There are 80 bones in the axial skeleton",
        "type": "TF"},
    "4": {
        "question": "When a living thing dies it DECOMPOSES and rots away. What does DECOMPOSE mean?",
        "options": ["to grow bigger", "to break down", "to survive", "to study closely"],
        "answer": "to break down",
        "hint": "",
        "type": "MCQ"},
    "5": {
        "question": "The energy from the Sun is an example of how light energy changes into ____________ energy.",
        "answer": "heat",
        "hint": "Sending the energy out into space as electromagnetic radiation, including visible light, heat, ultraviolet light, and radio waves.",
        "type": "QN"},
    "6": {
        "question": "Identify the following.",
        "image": "http://www.thetraveltart.com/wp-content/uploads/2011/01/General-Sherman-Tree.jpg",
        "answer": "sherman tree",
        "hint": "Largest tree in the world.",
        "type": "IMG"},
    "7": {
        "question": "True or False? The human skeleton is made up of less than 100 bones.",
        "answer": False,
        "hint": "There are 80 bones in the axial skeleton",
        "type": "TF"},
    }

#SLOT_LIST = ["question_a", "img_question_a", "mcq_question_a", "tf_question_a"]
#Qns-Ans slot list
QN_SLOTS = ["question_a", "gen_answer_a", "hint_a", "question_b", "gen_answer_b", "hint_b", 
            "question_c", "gen_answer_c", "hint_c", "question_d", "gen_answer_d", "hint_d",
            "question_e", "gen_answer_e", "hint_e", "question_f" ,"gen_answer_f", "hint_f", 
            "question_g", "gen_answer_g", "hint_g", "question_h", "gen_answer_h", "hint_h", 
            "question_i", "gen_answer_i", "hint_i", "question_j", "gen_answer_j", "hint_j"]

#Img Qns slot list
IMG_SLOTS = ["img_question_a", "img_url_a", "img_gen_answer_a", "img_hint_a", 
             "img_question_b", "img_url_b", "img_gen_answer_b", "img_hint_b", 
             "img_question_c", "img_url_c", "img_gen_answer_c", "img_hint_c", 
             "img_question_d", "img_url_d", "img_gen_answer_d", "img_hint_d", 
             "img_question_e", "img_url_e", "img_gen_answer_e", "img_hint_e",
             "img_question_f", "img_url_f", "img_gen_answer_f", "img_hint_f", 
             "img_question_g", "img_url_g", "img_gen_answer_g", "img_hint_g", 
             "img_question_h", "img_url_h", "img_gen_answer_h", "img_hint_h", 
             "img_question_i", "img_url_i", "img_gen_answer_i", "img_hint_i", 
             "img_question_j", "img_url_j", "img_gen_answer_j", "img_hint_j"]

#MCQ Qns slot list
MCQ_SLOTS = ["mcq_question_a", "qa_opt_a", "qa_opt_b", "qa_opt_c", "qa_opt_d", "mcq_gen_answer_a", "mcq_hint_a", 
             "mcq_question_b", "qb_opt_a", "qb_opt_b", "qb_opt_c", "qb_opt_d", "mcq_gen_answer_b", "mcq_hint_b", 
             "mcq_question_c", "qc_opt_a", "qc_opt_b", "qc_opt_c", "qc_opt_d", "mcq_gen_answer_c", "mcq_hint_c", 
             "mcq_question_d", "qd_opt_a", "qd_opt_b", "qd_opt_c", "qd_opt_d", "mcq_gen_answer_d", "mcq_hint_d",
             "mcq_question_e", "qe_opt_a", "qe_opt_b", "qe_opt_c", "qe_opt_d", "mcq_gen_answer_e", "mcq_hint_e",
             "mcq_question_f", "qf_opt_a", "qf_opt_b", "qf_opt_c", "qf_opt_d", "mcq_gen_answer_f", "mcq_hint_f", 
             "mcq_question_g", "qg_opt_a", "qg_opt_b", "qg_opt_c", "qg_opt_d", "mcq_gen_answer_g", "mcq_hint_g", 
             "mcq_question_h", "qh_opt_a", "qh_opt_b", "qh_opt_c", "qh_opt_d", "mcq_gen_answer_h", "mcq_hint_h", 
             "mcq_question_i", "qi_opt_a", "qi_opt_b", "qi_opt_c", "qi_opt_d", "mcq_gen_answer_i", "mcq_hint_i", 
             "mcq_question_j", "qj_opt_a", "qj_opt_b", "qj_opt_c", "qj_opt_d", "mcq_gen_answer_j", "mcq_hint_j"]

#True/ False Qns slot list
TF_SLOTS = ["tf_question_a", "tf_gen_answer_a", "tf_hint_a", "tf_question_b", "tf_gen_answer_b", "tf_hint_b", 
            "tf_question_c", "tf_gen_answer_c", "tf_hint_c", "tf_question_d", "tf_gen_answer_d", "tf_hint_d",
            "tf_question_e", "tf_gen_answer_e", "tf_hint_e", "tf_question_f", "tf_gen_answer_f", "tf_hint_f", 
            "tf_question_g", "tf_gen_answer_g", "tf_hint_g", "tf_question_h", "tf_gen_answer_h", "tf_hint_h", 
            "tf_question_i", "tf_gen_answer_i", "tf_hint_i", "tf_question_j", "tf_gen_answer_j", "tf_hint_j"]


#Qns-Ans slot list
QN_ANS_SLOTS = ["answer_a", "answer_b", "answer_c", "answer_d", "answer_e",
            "answer_f", "answer_g", "answer_h", "answer_i", "answer_j"]

#Img Ans slot list
IMG_ANS_SLOTS = ["img_answer_a", "img_answer_b", "img_answer_c", "img_answer_d", "img_answer_e",
                 "img_answer_f", "img_answer_g", "img_answer_h", "img_answer_i", "img_answer_j"]

#MCQ Ans slot list
MCQ_ANS_SLOTS = ["mcq_answer_a", "mcq_answer_b", "mcq_answer_c", "mcq_answer_d", "mcq_answer_e",
                 "mcq_answer_f", "mcq_answer_g", "mcq_answer_h", "mcq_answer_i", "mcq_answer_j"]

#True/ False Ans slot list
TF_ANS_SLOTS = ["tf_answer_a", "tf_answer_b", "tf_answer_c", "tf_answer_d", "tf_answer_e",
                "tf_answer_f", "tf_answer_g", "tf_answer_h", "tf_answer_i", "tf_answer_j"]


QUESTIONS = []  #Qns list
TF_QUESTIONS = []   #True/ False Qns list
IMG_QUESTIONS = []  #Img Qns list      
MCQ_QUESTIONS = []  #MCQ Qns list



class ActionSetupQns(Action):

    def name(self) -> Text:
        return "action_setup_questions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Setting Slots for Questions!!!")

        #extracting different type of questions
        for x in QUESTION_LIST.values():
            if x["type"] == "IMG":
                IMG_QUESTIONS.append(x["question"])
                IMG_QUESTIONS.append(x["image"])
                IMG_QUESTIONS.append(x["answer"])
                IMG_QUESTIONS.append(x["hint"])
            elif x["type"] == "MCQ":
                MCQ_QUESTIONS.append(x["question"])
                [MCQ_QUESTIONS.append(opt) for opt in x["options"]]
                MCQ_QUESTIONS.append(x["answer"])
                MCQ_QUESTIONS.append(x["hint"])
            elif x["type"] == "TF":
                TF_QUESTIONS.append(x["question"])
                TF_QUESTIONS.append(x["answer"])
                TF_QUESTIONS.append(x["hint"])
            else:
                QUESTIONS.append(x["question"])
                QUESTIONS.append(x["answer"])
                QUESTIONS.append(x["hint"])
        
        #setting qns-ans type question slots
        print("\n\nQns-Ans list: ", QUESTIONS)

        return [SlotSet(slot, qus) for (slot, qus) in zip(QN_SLOTS, QUESTIONS)]


class ActionSetupTfQn(Action):

    def name(self) -> Text:
        return "action_setup_tf_questions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #setting true/false type question slots
        print("\nTrue or False list: ", TF_QUESTIONS)

        return [SlotSet(slot, qus) for (slot, qus) in zip(TF_SLOTS, TF_QUESTIONS)]


class ActionSetupImgQn(Action):

    def name(self) -> Text:
        return "action_setup_img_questions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # setting img type question slots
        print("\nImg Qns list: ", IMG_QUESTIONS)

        return [SlotSet(slot, qus) for (slot, qus) in zip(IMG_SLOTS, IMG_QUESTIONS)]


class ActionSetupMcqQn(Action):

    def name(self) -> Text:
        return "action_setup_mcq_questions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #setting mcq type question slots
        print("\nMCQ Qns list: ", MCQ_QUESTIONS)

        return [SlotSet(slot, qus) for (slot, qus) in zip(MCQ_SLOTS, MCQ_QUESTIONS)]



class ActionQuizSetup(Action):

    def name(self) -> Text:
        return "action_quiz_setup"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Preparing Quiz Now!!!")

        #initializing mapped_slots, quiz_ans_slots, question_count 
        if len(mapped_slots) != 0:
            mapped_slots.clear()
        if len(quiz_ans_slots) != 0:
            quiz_ans_slots.clear()
        question_count = 0

        qns_total = len(QUESTIONS)
        tf_total = len(TF_QUESTIONS)
        img_total = len(IMG_QUESTIONS) 
        mcq_total = len(MCQ_QUESTIONS)
        count = 1

        #mapping qns-ans type to slots
        y = 0
        for x in range(0,qns_total,3):
            mapped_slots[str(count)] = {
                "question": QN_SLOTS[x],
                "gen-answer": QN_SLOTS[x+1],
                "hint": QN_SLOTS[x+2],
                "answer": QN_ANS_SLOTS[y]
            }
            count= count+1
            y = y+1  
        
        #mapping true/false type to slots
        y = 0
        for x in range(0,tf_total,3):
            mapped_slots[str(count)] = {
                "question": TF_SLOTS[x],
                "gen-answer": TF_SLOTS[x+1],
                "hint": TF_SLOTS[x+2],
                "answer": TF_ANS_SLOTS[y]
            }
            count= count+1  
            y = y+1  

        #mapping img type to slots
        y = 0
        for x in range(0,img_total,4):
            mapped_slots[str(count)] = {
                "question": IMG_SLOTS[x],
                "gen-answer": IMG_SLOTS[x+2],
                "hint": IMG_SLOTS[x+3],
                "answer": IMG_ANS_SLOTS[y]
            }
            count= count+1 
            y = y+1     

        #mapping mcq type to slots
        y = 0
        for x in range(0,mcq_total,7):
            mapped_slots[str(count)] = {
                "question": MCQ_SLOTS[x],
                "gen-answer": MCQ_SLOTS[x+5],
                "hint": MCQ_SLOTS[x+6],
                "answer": MCQ_ANS_SLOTS[y]
            }
            count= count+1 
            y = y+1     

        question_count = count - 1  
        print("\n\nMapped Slots: ", mapped_slots)
        [quiz_ans_slots.append(x["answer"]) for x in mapped_slots.values()]
        print("\nAnswer slots: ", quiz_ans_slots)

        random.shuffle(quiz_ans_slots)
        print("Answer slots(shuffled): ", quiz_ans_slots, "\n")

        return []


class ScienceQuizForm(FormAction):

    def name(self) -> Text:
        return "science_quiz_form"

    @staticmethod 
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        
        #return ["answer_a", "img_answer_a", "mcq_answer_a", "tf_answer_a"]  [x for x in quiz_ans_slots]
        return quiz_ans_slots

    #TODO: continue to update actions/form from here
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        # return {
        #     "answer_a": [self.from_entity(
        #         entity="answer_a",
        #         intent="inform"),
        #         self.from_text()],
        #     "img_answer_a": [self.from_entity(
        #         entity="img_answer_a",
        #         intent="inform"),
        #         self.from_text()],
            # "mcq_answer_a": [self.from_entity(
            #     entity="mcq_answer_a",
            #     intent="inform"),
            #     self.from_text()],
        #     "tf_answer_a": [self.from_text()]
        # }        
        
        result = {}        
        for item in quiz_ans_slots:
            result[item] = [
                self.from_entity(entity=item),
                self.from_text()]

        return result


    def submit(
        self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict]:
        """define what the form has to do after all the 
            required slots are filled"""

        #utter submit template
        dispatcher.utter_message(template="utter_submit")
        i = 1
        res = "Here are your answers in the quiz:\n"
        for x in quiz_ans_slots:
            ans = tracker.get_slot(x)
            res = res + "Question({}): {}\n".format(i, ans)
            i += 1
        dispatcher.utter_message(text=res)

        return []


class CalculateScore(Action):
    """Detect users dialect"""

    def name(self) -> Text:
        return "action_calculate_score"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """place holder method for guessing dialect"""

        dispatcher.utter_message(template="utter_working_on_it")
        bug_slot_info = tracker.get_slot("answer_a")
        #print(bug_slot_info)

        return [SlotSet("score", 100)]


# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
