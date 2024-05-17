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
Output in the list format like [medicalTermA, medicalTermB, medicalTermC].
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
        except:
            validUrl = False

        return validUrl

    def explain_med_term(self, speak, error="None"):

        prompt1 = f"""
Explain the following **medical terms** in no more than two sentences in {self.lan} simply.
No more extra output. Just simply explanation output.
If another language is entered, please explain the word in {self.lan}.
If another unexpected input occurs like a sentence, output {error}.
"""

        # Creating Chatbot Instances
        exp = connect_gpt.ChatBot(self.lan, prompt1)
        res1 = exp.speak_to_gpt(speak)

        prompt2 = f"""
Output only the **URL** of the site that explains the following medical term in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
If the website cannot be found, it is also acceptable to output the URL of Wikipedia.
"""

        link = connect_gpt.ChatBot(self.lan, prompt2)
        res2 = link.speak_to_gpt(speak)

        words = res2.split()
        res3 = error
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                url = word
                if self.check_url(url):
                    res3 = url
                break

        print("last: " + res3)
        return {"exp":res1, "link":res3}

if __name__ == "__main__":

    HL = highlighter("English")
    for i in range(5):

        str2 = input(">>")
        res2 = HL.explain_med_term(str2)
        #res1 = HL.search_med_term(str2)
