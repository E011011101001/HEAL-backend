# This code has two functions.

# Use "search_med_term" method to obtain a response from gpt for medical term extraction.
# Use "explain_med_term" method to get an explanation of medical terms.

import connect_gpt

def search_med_term(lan, speak):

    prompt = """
次の文章から医療専門用語を取り出して列挙してください。
"""

    # Creating Chatbot Instances
    smt = connect_gpt.ChatBot(lan, prompt)
    res = smt.speak_to_gpt(speak)

    return res

def explain_med_term(lan, speak):

    prompt = """
次の医療用語を説明してください。
"""

    # Creating Chatbot Instances
    smt = connect_gpt.ChatBot(lan, prompt)
    res = smt.speak_to_gpt(speak)

    return res
