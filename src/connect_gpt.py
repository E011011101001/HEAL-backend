import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

#language variable
#use history(assistant) variable
#chat id?

#receive sentence
class ChatBot:
    def __init__(self, language, history):

        self.lan = language
        #string

        self.hist = history
        #dict [{"text": contents, "speaker": "user" or "assistant"}, ...]

    def speak_to_gpt(self, utterance):
        print(f"Received {utterance}")

        system_content1 = "You are about to have a conversation with a patient who is troubled by certain symptoms. Ask for details about the symptoms and how they came about."
        system_content2 = "Avoid private questions like personal information. Please respond in "+ self.lan +"."
        user_content = utterance

        messages=[
            {"role": "system", "content": system_content1},
            {"role": "system", "content": system_content2}
        ]

        for textTaple in self.hist:
            messages.append({"role": textTaple["speaker"], "content": textTaple["text"]})

        messages.append({"role": "user", "content": user_content})

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    
        pol_msg = response.choices[0].message.content
        response = pol_msg

        print(f"Send: {response}")

        return response
            

if __name__ == "__main__":

    tmpHistory = [{"text":"My chest hurts.", "speaker": "user"}, 
                  {"text":"I'm sorry to hear that. Can you tell me more about your symptoms? When did the chest pain start? Have you experienced any other symptoms along with the chest pain?", "speaker":"assistant"}]

    gpt1 = ChatBot("English", [])
    gpt1.speak_to_gpt("My chest hurt.")

