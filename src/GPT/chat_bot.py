# This class takes a language and prompt as arguments and creates an instance.
#   gpt = ChatBot("Japanese", "You are a doctor. Ask for details about the symptoms.")

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def send_msg_to_gpt(messages):
    response = openai.chat.completions.create(
        model="gpt-4o",  # change to gpt-4 for the most professional AI doctor
        messages=messages,
        temperature=0.1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content


class ChatBot:
    def __init__(self, language: str, init_prompt: str):
        self.lan = language
        lan_prompt = f"Please respond in the language corresponding to the language code `{self.lan}`."
        self.prompt = init_prompt + ' ' + lan_prompt

        self.messages = [
            {"role": "system", "content": self.prompt}
        ]

    def chat(self, msg: str):
        self.messages.append({"role": "user", "content": msg})

        assistant_msg = send_msg_to_gpt(self.messages)
        self.messages.append({"role": "assistant", "content": assistant_msg})

        return assistant_msg


if __name__ == "__main__":

    prompt = ("You are about to have a conversation with a patient who is troubled by certain symptoms. Ask for "
              "details about the symptoms and how they came about.")

    gpt1 = ChatBot("English", prompt)
    print('')
    for i in range(10):
        input_msg = input('<< ')
        print(f'>> {gpt1.chat(input_msg)}')
