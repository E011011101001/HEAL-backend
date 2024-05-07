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
次の文章から**医療専門用語だけ**を取り出し、コンマ区切りで列挙してください。
"""

        # Creating Chatbot Instances
        smt = connect_gpt.ChatBot(self.lan, prompt)
        res = smt.speak_to_gpt(speak)

        return res

    def explain_med_term(self, speak):

        prompt1 = """
次の医療用語を３文程度で説明してください。
"""

        # Creating Chatbot Instances
        exp = connect_gpt.ChatBot(self.lan, prompt1)
        res1 = exp.speak_to_gpt(speak)

        prompt2 = """
１．指定した用語が詳しく説明されている**リンク先**を調べてください。
リンク先が提供できない場合は、**空白**を出力すること。
２．リンク先のページに指定された用語の説明が本当にあるか確認してください。
３．確認できた場合のみ、**リンク先だけ**を出力してください。
"""
        link = connect_gpt.ChatBot(self.lan, prompt2)
        res2 = link.speak_to_gpt(speak)

        return {"exp":res1, "link":res2}

if __name__ == "__main__":

    HL = highlighter("English")
    for i in range(5):

        str2 = input(">>")
        res2 = HL.explain_med_term(str2)