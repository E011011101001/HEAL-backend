# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

# do we need history?

import connect_gpt
import urllib.request

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
        smt = connect_gpt.ChatBot("input language", prompt)
        res = smt.speak_to_gpt(speak)

        return res

    def check_url(self, url):
        validUrl = True
        try:
            tmp = urllib.request.urlopen(url)
            tmp.close()
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code}")
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
        exp = connect_gpt.ChatBot(self.lan, prompt_exp)
        res1 = exp.speak_to_gpt(speak)

        prompt_url = f"""
Output only the **URL** of the site that explains the following medical term in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
Please try to refer to the most reliable sites possible about following medical term.
"""
        prompt_wiki_url = f"""
Output only the **wikipedia URL** that explains the following medical term in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
For example, when language code is ja, inputting リウマチ熱, output https://ja.wikipedia.org/wiki/%E3%83%AA%E3%82%A6%E3%83%9E%E3%83%81%E7%86%B1
"""

        link = connect_gpt.ChatBot(self.lan, prompt_url)
        res2 = link.speak_to_gpt(speak)

        #words = res2.split()
        res3 = error
        #for word in words:
        #    if word.startswith("http://") or word.startswith("https://"):
        #        url = word

        if self.check_url(res2):
            res3 = res2
        else:
            link = connect_gpt.ChatBot(self.lan, prompt_wiki_url)
            res2 = link.speak_to_gpt(speak)

            if self.check_url(res2):
                res3 = res2

        return {"exp":res1, "link":res3}

    def get_synonym(self, term, error="None"):
        prompt_syn = f"""
List synonyms that have exactly the same meaning as {term} in {self.lan}.
Output in the list format like synonymA,synonymB,synonymC.
No more extra output. Just simply list output.
If there are no synonyms terms or unexpected input occurs, output {error}.
"""
        syn = connect_gpt.ChatBot(self.lan, prompt_syn)
        res = syn.speak_to_gpt(term)

        return res

if __name__ == "__main__":

    HL = highlighter("jp")
    for i in range(5):

        str2 = input(">>")
        res2 = HL.explain_med_term(str2)
        print(res2)
        res3 = HL.get_synonym(str2)
        print(res3)

        #res1 = HL.search_med_term(str2)
