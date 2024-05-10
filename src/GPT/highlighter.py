# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

# do we need history?

import connect_gpt
import urllib.request

class highlighter():
    def __init__(self, lan, history=[]):

        self.lan = lan
        self.log = []

        userText = True
        for text in history:
            if userText:
                self.log.append({"text":text, "speaker": "user"})
            else:
                self.log.append({"text":text, "speaker": "assistant"})

            userText = not userText

    def search_med_term(self, speak):

        prompt = """
次の文章の中にある**医療に関する専門用語**を取り出し、コンマ区切りで列挙してください。
"""

        # Creating Chatbot Instances
        smt = connect_gpt.ChatBot(self.lan, prompt)
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

    def explain_med_term(self, speak):

        prompt1 = """
次の医療用語を２文程度で説明してください。
"""

        # Creating Chatbot Instances
        exp = connect_gpt.ChatBot(self.lan, prompt1)
        res1 = exp.speak_to_gpt(speak)

        prompt2 = """
指定した用語について説明されているサイトの**URLだけ**を出力してください。ただし、次の言語で書かれたサイトを出力してください。
言語："""+self.lan+"""

どうしてもサイトが見つからなければWikipediaのurlを出力しても構いません
"""

        link = connect_gpt.ChatBot(self.lan, prompt2)
        res2 = link.speak_to_gpt(speak)

        words = res2.split()
        res3 = ""
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
        # res1 = HL.search_med_term(str2)
