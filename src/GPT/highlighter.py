# src/GPT/highlighter.py
import urllib.request
from .chatbot import ChatBot

class highlighter:
    def __init__(self, lan, history=[]):
        language_dict = {'en': 'English', 'ja': 'Japanese', 'jp': 'Japanese', 'cn': 'Chinese'}
        self.lan = language_dict.get(lan, lan)
        self.log = []

        userText = True
        for text in history:
            if userText:
                self.log.append({"text": text, "speaker": "user"})
            else:
                self.log.append({"text": text, "speaker": "assistant"})

            userText = not userText

    def search_med_term(self, speak, error="None"):
        prompt = f"""
Extract the medical terms from the following text and list them separated by commas.
Output in the list format like medicalTermA,medicalTermB,medicalTermC.
No more extra output. Just simply list output.
If there are no medical terms or unexpected input occurs, output {error}.
"""
        smt = ChatBot("input language", prompt)
        res = smt.chat(speak)
        return res

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
        prompt1 = f"""
Explain the following **medical terms** in a sentence in {self.lan} simply.
No more extra output. Just simply explanation output.
If another language is entered, please explain the word in {self.lan}.
If another unexpected input occurs like a sentence, output {error}.
"""
        exp = ChatBot(self.lan, prompt1)
        res1 = exp.chat(speak)

        prompt2 = f"""
Output only the **URL** of the site that explains the following medical term in {self.lan}.
No more extra output. Just simply URL output.
If unexpected input occurs like long sentences, output {error}.
If the website cannot be found, it is also acceptable to output the URL of Wikipedia, but please try to refer to the most reliable sites possible.
"""
        link = ChatBot(self.lan, prompt2)
        res2 = link.chat(speak)

        words = res2.split()
        res3 = error
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                url = word
                if self.check_url(url):
                    res3 = url
                break
        return {"exp": res1, "link": res3}

if __name__ == "__main__":
    HL = highlighter("English")
    for i in range(5):
        str2 = input(">>")
        res2 = HL.explain_med_term(str2)
