# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

# do we need history?

import connect_gpt

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
次の文章から医療専門用語を取り出して列挙してください。
"""

        # Creating Chatbot Instances
        smt = connect_gpt.ChatBot(self.lan, prompt)
        res = smt.speak_to_gpt(speak)

        return res

    def explain_med_term(self, speak):

        prompt = """
次の医療用語を説明してください。
また、指定する言語でWikipediaのリンク先を出力してください。
"""

        # Creating Chatbot Instances
        smt = connect_gpt.ChatBot(self.lan, prompt)
        res = smt.speak_to_gpt(speak)

        return res
