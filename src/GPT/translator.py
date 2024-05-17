import connect_gpt

def translate(lan, speak, user='PATIENT', errorString="error"):

    # DOCTOR -> PATIENT translate
    if user=='PATIENT':
        prompt = f"""
Following sentence is directed from a doctor to a patient.
Translate the following sentences accurately into {lan}.
No more extra output. Just simply translated output.
During the interaction, if there is anything unexpected or any other error, please only output "{errorString}"
"""
    if user=='DOCTOR':
        prompt = f"""
Following sentence is directed from a patient to a doctor.
Translate the following sentences accurately into {lan}.
No more extra output. Just simply translated output.
During the interaction, if there is anything unexpected or any other error, please only output "{errorString}"
"""
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
