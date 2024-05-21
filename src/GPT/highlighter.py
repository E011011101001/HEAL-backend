# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

# do we need history?
import json

import urllib.request
from . import ChatBot
#from .translator import translate_to

import openai
import os
import ast

openai.api_key = os.getenv("OPENAI_API_KEY")

extractors: dict[str, ChatBot] = {}
synonymGetters: dict[str, ChatBot] = {}
typeGetters: dict[str, ChatBot] = {}
explainers: dict[str, ChatBot] = {}
urlGetters: dict[str, ChatBot] = {}
wikiUrlGetters: dict[str, ChatBot] = {}


def search_med_term(lan_code, text, error="None"):
    global extractors

    prompt = f"""
Extract specialized medical terms from the following text and list them separated by commas.
Output in the list format like medicalTermA,medicalTermB,medicalTermC.
Make sure to extract only what is present in the text.
No more extra output. Just simply list output.
If there are no medical terms or unexpected input occurs, output {error}.
"""
    # Creating Chatbot Instances
    extractor = extractors.get(lan_code)

    if extractor is None:
        extractor = ChatBot(lan_code, prompt)
        extractors[lan_code] = extractor

    res = extractor.chat(text)

    if res == error:
        return []

    resList = res.split(",")
    return resList

def get_synonym(lan_code, term, error="None"):
    global synonymGetters

    prompt_syn = f"""
List synonyms that have the same meaning as {term} in {lan_code}.
Output in the list format like synonymA,synonymB,synonymC.
No more extra output. Just simply list output.
If there are no synonyms terms or unexpected input occurs, output {error}.
"""
    synonymGetter = synonymGetters.get(lan_code)

    if synonymGetter is None:
        synonymGetter = ChatBot(lan_code, prompt_syn)
        synonymGetters[lan_code] = synonymGetter

    res = synonymGetter.chat(term)

    if res == error:
        return []

    resList = res.split(",")
    return resList

def get_termType(lan_code, term, error="GENERAL"):
    global typeGetters

    prompt_type = f"""
Classify the following medical terms into one of the three categories: 'CONDITION,' 'PRESCRIPTION,' or 'GENERAL'.
No more extra output. Just simply categories output like "CONDITION".
If another unexpected input occurs like a sentence, output {error}.
"""
    typeGetter = typeGetters.get(lan_code)
    if typeGetter is None:
        typeGetter = ChatBot(lan_code, prompt_type)
        typeGetters[lan_code] = typeGetter

    res = typeGetter.chat(term)

    return res

def explain_med_term(lan_code, term, error="None"):
    global explainers

    prompt_exp = f"""
Explain the following **medical terms** in a sentence in {lan_code} simply.
No more extra output. Just simply explanation output.
If another language is entered, please explain the word in {lan_code}.
If another unexpected input occurs like a sentence, output {error}.
"""
    explainer = explainers.get(lan_code)

    if explainer is None:
        explainer = ChatBot(lan_code, prompt_exp)
        explainers[lan_code] = explainer

    res = explainer.chat(term)

    return res

def check_url(url):
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

def get_url(lan_code, term, error="None"):
    # chatgpt CANNOT confirm the site of link
    # if getting only wikipedia is OK, just prompt_wiki_url is enough
    global urlGetters
    global wikiUrlGetters

    prompt_url = f"""
Output only the **URL** of the site that **certainly explains the following medical term** in {lan_code}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
Please try to refer to the most reliable sites about following medical term.
"""
    prompt_wiki_url = f"""
Output only the **wikipedia URL** that explains the following medical term in {lan_code}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
For example, when language code is jp, inputting リウマチ熱, output https://ja.wikipedia.org/wiki/%E3%83%AA%E3%82%A6%E3%83%9E%E3%83%81%E7%86%B1
"""

    urlGetter = urlGetters.get(lan_code)
    if urlGetter is None:
        urlGetter = ChatBot(lan_code, prompt_url)
        urlGetters[lan_code] = urlGetter

    res = urlGetter.chat(term)

    urlstr = error

    if check_url(res):
        urlstr = res
    else:
        wikiUrlGetter = wikiUrlGetters.get(lan_code)
        if wikiUrlGetter is None:
            wikiUrlGetter = ChatBot(lan_code, prompt_wiki_url)
            wikiUrlGetters[lan_code] = wikiUrlGetter

        res = wikiUrlGetter.chat(term)

        if check_url(res):
            urlstr = res

    return urlstr

class Highlighter():
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

    def search_translated_med_term(self, trans_text, original_text, termList, error="None"):
        #[A, B, C]
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

        #[[A, tA],[B, tB],[C, tC]]
        return resList

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

    HL = Highlighter("jp")
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
