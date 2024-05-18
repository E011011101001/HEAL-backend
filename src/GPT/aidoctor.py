# This code has a function that responds to a statement in a chatbot query.
# There may be room for improvement since an object is generated each time in one exchange.

# "__create_log" method creates a formatted history. If we connect to a database, this may no longer be necessary.

# Use "communicate_qst" method to obtain a response from gpt for a query.
#   speak = "I am fine"
#   log = [
#       {"text":"Hello", "speaker": "user"},
#       {"text":"Hello! Are you feeling unwell today?", "speaker":"assistant"}
#   ]
#   response = communicate_qst("English", speak, history)

# create class
# export_history
# history -string

import connect_gpt


def create_log(user_msg, ai_msg, log):
    log.append({"text": user_msg, "speaker": "user"})
    log.append({"text": ai_msg, "speaker": "assistant"})

    return log


class AIDoctor():
    prompt = """これからあなたは問診を行ってもらいます。
箇条書きされる質問について対話形式で質問を行ってください。
ただし、一度のメッセージでは一言で回答できる質問だけをしてください。その際に括弧の中の選択肢を与えてください。
一回の出力では質問を**ひとつだけ**出力してください。

全ての質問が終了したときは、情報をまとめて箇条書きで表示してください。

・具合の悪いところをどこがどのように悪いか
・症状はいつからか
・今までにかかったことのある病気や治療中の病気はあるか（１喘息・２高血圧・３糖尿病・４心臓病・５その他）
・（あるなら）それはいつごろか
・今までに手術や輸血の経験はあるか（１ある・２なし）
・（あるなら）それはいつ頃か
・（あるなら）そのときの病名は何か
・現在服用している薬はあるか（１ある・２なし）
・（あるなら）薬の名前は何か
・たばこは吸うか（１吸わない・２吸う・３過去に吸っていた）
・（吸うなら）１日何本吸っているか
・（吸うなら）約何年間吸っているか
・アルコールは摂取するか（１飲まない・２飲む）
・（飲むなら）種類は何か
・（飲むなら）１回何杯程度飲んでいるか
・（飲むなら）頻度はどうか（１毎日・２時々・３月２～３回）
"""

    def __init__(self, lan, log=None):
        if log is None:
            self.log = []
        else:
            self.log = log

        self.lan = lan

    def send_and_get_reply(self, message):

        self.log.append({"text": message, "speaker": "user"})

        # Creating Chatbot Instances
        bot = connect_gpt.ChatBot(self.lan, self.prompt)
        ai_msg = bot.speak_to_gpt_with_log(message, self.log)

        self.log.append({"text": ai_msg, "speaker": "assistant"})

        return ai_msg

    def export_history(self):
        history = []
        for textTaple in self.log:
            history.append(textTaple["text"])

        return history


if __name__ == "__main__":

    # new questioner chat
    Qst = AIDoctor("English")
    for i in range(5):
        str = input(">>")
        res = Qst.send_and_get_reply(str)

    # generate log
    log = Qst.export_history()

    # questioner chat using log
    Qst2 = AIDoctor("English", log)
    for i in range(20):
        str = input(">>")
        res = Qst2.send_and_get_reply(str)
