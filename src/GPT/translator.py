import connect_gpt

def translate(lan, speak, user='PATIENT'):

    # DOCTOR -> PATIENT translate
    if user=='PATIENT':
        prompt = "Following sentence is directed from a doctor to a patient." + "Translate the following sentences accurately into "+lan+"."

    if user=='DOCTOR':
        prompt = "Following sentence is directed from a patient to a doctor." + "Translate the following sentences accurately into "+lan+"."

    # Creating Chatbot Instances
    tl = connect_gpt.ChatBot(lan, prompt)
    res = tl.speak_to_gpt(speak)

    return res

if __name__ == "__main__":

    for i in range(5):

        str1 = input(">>")
        res1 = translate("Japanese", str1)

        str2 = input(">>")
        res2 = translate("English", str2, 'DOCTOR')
