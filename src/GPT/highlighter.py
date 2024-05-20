# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

# do we need history?
import json

import urllib.request
#from . import ChatBot
#from .translator import translate_to

import openai
import os
import ast

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, language, prompt):

        self.lan = language     #string

        self.prompt = prompt    #string
        self.system_content1 = self.prompt

    #private function
    # model = gpt-3.5-turbo
    # model = gpt-4-0125-preview
    def __send_msg_to_gpt(self, messages):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        pol_msg = response.choices[0].message.content
        response = pol_msg

        return response

    def speak_to_gpt(self, utterance):

        messages=[
            {"role": "system", "content": self.system_content1},
            {"role": "user", "content": utterance}
        ]

        return self.__send_msg_to_gpt(messages)

    def speak_to_gpt_with_log(self, utterance, history):

        messages=[
            {"role": "system", "content": self.system_content1},
            {"role": "system", "content": self.system_content2}
        ]

        for textTaple in history:
            messages.append({"role": textTaple["speaker"], "content": textTaple["text"]})

        messages.append({"role": "user", "content": utterance})

        return self.__send_msg_to_gpt(messages)

translators = {}


def translate(lan, speak, user='PATIENT', errorString="error"):

    language_dict = {'en': 'English', 'ja': 'Japanese', 'jp': 'Japanese', 'cn': 'Chinese'}
    lan = language_dict.get(lan, lan)

    # DOCTOR -> PATIENT translate
    if user=='PATIENT':
        prompt = f"""
Following sentence is directed from a doctor to a patient.
Translate the following sentences accurately into {lan}.
No more extra output. Just simply translated output.
During the interaction, if there is anything unexpected or any other error, please only output "{errorString}"
"""
    if user=='DOCTOR':
        prompt = f"""
Following sentence is directed from a patient to a doctor.
Translate the following sentences accurately into {lan}.
No more extra output. Just simply translated output.
During the interaction, if there is anything unexpected or any other error, please only output "{errorString}"
"""
    # Creating Chatbot Instances
    tl = ChatBot(lan, prompt)
    res = tl.speak_to_gpt(speak)
    return res

class highlighter():
    def __init__(self, lan, history=[]):
        language_dict = {'en': 'English', 'ja': 'Japanese', 'jp': 'Japanese', 'cn': 'Chinese'}
        self.lan = language_dict.get(lan, lan)
        self.log = []

        userText = True
        for text in history:
            if userText:
                self.log.append({"text":text, "speaker": "user"})
            else:
                self.log.append({"text":text, "speaker": "assistant"})

            userText = not userText

    def search_med_term(self, speak, error="None"):

        prompt = f"""
Extract the medical terms from the following text and list them separated by commas.
Output in the list format like medicalTermA,medicalTermB,medicalTermC.
No more extra output. Just simply list output.
If there are no medical terms or unexpected input occurs, output {error}.
"""

        # Creating Chatbot Instances
        smt = ChatBot("input language", prompt)
        res = smt.speak_to_gpt(speak)

        if res == error:
            return []

        resList = res.split(",")
        return resList

    def search_translated_med_term(self, speak, original_text, termList, error="None"):

        prompt = f"""
The medical term list {termList} is extracted from the text "{original_text}".
Extract terms with the same meaning from the following text written in different languages in the same order.
Output in the list format like [['medicalTermA_in_termList','translatedMedicalTermA'],['medicalTermB_in_termList','translatedMedicalTermB']].
Output list size must be equal to the medical term list size.
No more extra output. Just simply list output.
If there are no medical terms or unexpected input occurs, output {error}.
"""

        # Creating Chatbot Instances
        smt = ChatBot("two input languages", prompt)
        res = smt.speak_to_gpt(speak)

        if res == error:
            return []

        resList = ast.literal_eval(res)
        return resList

    def check_url(self, url):
        validUrl = True
        try:
            tmp = urllib.request.urlopen(url)
            tmp.close()
        except urllib.error.HTTPError as e:
            if e.code == 403:  # Forbidden Error
                return True
            else:
                return False
        except Exception as e:
            return False

        return validUrl

    def explain_med_term(self, speak, error="None"):

        prompt_exp = f"""
Explain the following **medical terms** in a sentence in {self.lan} simply.
No more extra output. Just simply explanation output.
If another language is entered, please explain the word in {self.lan}.
If another unexpected input occurs like a sentence, output {error}.
"""

        # Creating Chatbot Instances
        exp = ChatBot(self.lan, prompt_exp)
        res = exp.speak_to_gpt(speak)

        return res

    def get_url(self, term, error="None"):
        prompt_url = f"""
Output only the **URL** of the site that **certainly explains the following medical term** in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
Please try to refer to the most reliable sites about following medical term.
"""
        prompt_wiki_url = f"""
Output only the **wikipedia URL** that explains the following medical term in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
For example, when language code is ja, inputting リウマチ熱, output https://ja.wikipedia.org/wiki/%E3%83%AA%E3%82%A6%E3%83%9E%E3%83%81%E7%86%B1
"""

        url = ChatBot(self.lan, prompt_url)
        res = url.speak_to_gpt(term)

        #words = res2.split()
        urlstr = error
        #for word in words:
        #    if word.startswith("http://") or word.startswith("https://"):
        #        url = word

        if self.check_url(res):
            urlstr = res
        else:
            link = ChatBot(self.lan, prompt_wiki_url)
            res2 = link.speak_to_gpt(term)

            if self.check_url(res2):
                urlstr = res2

        return urlstr

    def get_synonym(self, term, error="None"):
        prompt_syn = f"""
List synonyms that have exactly the same meaning as {term} in {self.lan}.
Output in the list format like 'synonymA','synonymB','synonymC'.
No more extra output. Just simply list output.
If there are no synonyms terms or unexpected input occurs, output {error}.
"""
        syn = ChatBot(self.lan, prompt_syn)
        res = syn.speak_to_gpt(term)

        if res == error:
            return []

        resList = res.split(",")
        return resList

    def get_termType(self, term, error="GENERAL"):
        prompt_type = f"""
Classify the following medical terms into one of the three categories: 'CONDITION,' 'PRESCRIPTION,' or 'GENERAL'.
No more extra output. Just simply categories output like "CONDITION".
If another unexpected input occurs like a sentence, output {error}.
"""
        typ = ChatBot(self.lan, prompt_type)
        res = typ.speak_to_gpt(term)

        return res

if __name__ == "__main__":

    HL = highlighter("jp")
    """
    for i in range(5):

        str2 = input(">>")
        res2 = HL.search_med_term(str2)
        print(res2)
        res3 = translate("jp", str2)
        print(res3)
        res4 = HL.search_translated_med_term(res3, str2, res2)
        print(res4)

        #res1 = HL.search_med_term(str2)
        """

    for i in range(5):

        str2 = input(">>")
        res1 = HL.get_termType(str2)
        print(res1)
        res2 = HL.get_synonym(str2)
        print(res2)
        res3 = HL.explain_med_term(str2)
        print(res3)
        res4 = HL.get_url(str2)
        print(res4)
