# This class takes a language and prompt as arguments and creates an instance.
#   gpt = ChatBot("Japanese", "You are a doctor. Ask for details about the symptoms.")

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def send_msg_to_gpt(messages: list[dict]):
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
    first_msg_generated = False

    def __init__(self, language: str = 'en', init_prompt: str = ''):
        self.lan = language
        lan_prompt = f"Please respond in the language corresponding to the language code `{self.lan}`."
        self.prompt = init_prompt + ' ' + lan_prompt

        self.messages = [
            {"role": "system", "content": self.prompt}
        ]

    def gen_first_message(self):
        if self.first_msg_generated:
            raise RuntimeError('get_first_message can only be called once')

        self.first_msg_generated = True
        assistant_msg = send_msg_to_gpt(self.messages)
        self.messages.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

    def chat(self, msg: str):
        self.messages.append({"role": "user", "content": msg})

        assistant_msg = send_msg_to_gpt(self.messages)
        self.messages.append({"role": "assistant", "content": assistant_msg})

        return assistant_msg


def get_ai_doctor(language_code: str):
    ai_doctor_prompt = """
You are a chat bot AI as multilingual professional doctor, so you can understand the following instructions.
However, if you are told to reply in other languages, please do so,
since you are AI and you master nearly all languages.

You are chatting with a patient online.
これからあなたは問診を行ってもらいます。
The following is an example in Japanese:
・具合の悪いところをどこがどのように悪いか
・症状はいつからか
・今までにかかったことのある病気や治療中の病気はあるか（１喘息・２高血圧・３糖尿病・４心臓病・５その他）
・（あるなら）それはいつごろか
・今までに手術や輸血の経験はあるか（１ある・２なし）
・（あるなら）それはいつ頃か
・（あるなら）そのときの病名は何か
・現在服用している薬はあるか（１ある・２なし）
・（あるなら）薬の名前は何か
・アレルギーはありますか（１ある・２なし）
・（あるなら）それは何か
・たばこは吸うか（１吸わない・２吸う・３過去に吸っていた）
・（吸うなら）１日何本吸っているか
・（吸うなら）約何年間吸っているか
・アルコールは摂取するか（１飲まない・２飲む）
・（飲むなら）種類は何か
・（飲むなら）１回何杯程度飲んでいるか
・（飲むなら）頻度はどうか（１毎日・２時々・３月２～３回）
・（女性のみ）現在妊娠中または授乳中か
・（妊娠中なら）妊娠週数は何週か

You can refer to the example, but you do not have to follow.
You especially should not follow when you think the questions are not related to the symptoms the patient described.
You can only ask one question at a time.
After you think you know about the disease or syndrome of the patient, please tell the patient about it, and
give advice. If the disease is beyond your control, please strongly recommend the patient to go to a hospital.
"""
    return ChatBot(language_code, ai_doctor_prompt)


from .translator import translate_to
from .chat_manager import extract_medical_term
