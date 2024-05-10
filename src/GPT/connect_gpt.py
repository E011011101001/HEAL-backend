# This class takes a language and prompt as arguments and creates an instance.
#   gpt = ChatBot("Japanese", "You are a doctor. Ask for details about the symptoms.")

# This class consists of two methods and one private method.

# Use "speak_to_gpt" method to obtain a response from gpt for a single text without referring to the history.
#   gpt.speak_to_gpt("My chest hurt.")

# Use "speak_to_gpt_with_log" method to refer to the history. The format of the history is assumed to be the following tuple (as of now).
#   history = [{"text":"My chest hurts.", "speaker": "user"}, {"text":"I'm sorry to hear that. When did the chest pain start?", "speaker":"assistant"}]
#   gpt.speak_to_gpt_with_log("1 hour ago.", history)

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, language, prompt):

        self.lan = language     #string

        self.prompt = prompt    #string

        self.system_content1 = self.prompt
        self.system_content2 = "Avoid private questions like personal information. Please respond in "+ self.lan +"."

    #private function
    # model = gpt-3.5-turbo
    # model = gpt-4-0125-preview
    def __send_msg_to_gpt(self, messages):
        response = openai.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        pol_msg = response.choices[0].message.content
        response = pol_msg

        print(f"Send: {response}")
        return response

    def speak_to_gpt(self, utterance):
        print(f"Received {utterance}")

        messages=[
            {"role": "system", "content": self.system_content1},
            {"role": "system", "content": self.system_content2},
            {"role": "user", "content": utterance}
        ]

        return self.__send_msg_to_gpt(messages)

    def speak_to_gpt_with_log(self, utterance, history):
        print(f"Received {utterance}")

        messages=[
            {"role": "system", "content": self.system_content1},
            {"role": "system", "content": self.system_content2}
        ]

        for textTaple in history:
            messages.append({"role": textTaple["speaker"], "content": textTaple["text"]})

        messages.append({"role": "user", "content": utterance})

        return self.__send_msg_to_gpt(messages)


if __name__ == "__main__":

    tmpHistory = [{"text":"My chest hurts.", "speaker": "user"},
                  {"text":"I'm sorry to hear that. Can you tell me more about your symptoms? When did the chest pain start? Have you experienced any other symptoms along with the chest pain?", "speaker":"assistant"}]

    prompt = "You are about to have a conversation with a patient who is troubled by certain symptoms. Ask for details about the symptoms and how they came about."

    gpt1 = ChatBot("English", prompt)
    gpt1.speak_to_gpt("My chest hurt.")
    gpt1.speak_to_gpt_with_log("1 hour ago.", tmpHistory)
