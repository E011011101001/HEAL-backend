import connect_gpt

def translate(lan, speak):

    prompt = "Translate following sentences in "+lan+"."

    # Creating Chatbot Instances
    tl = connect_gpt.ChatBot(lan, prompt)
    res = tl.speak_to_gpt(speak)

    return res