# This code has a function that responds to a statement in a chatbot query.
# There may be room for improvement since an object is generated each time in one exchange.

# "__create_log" method creates a formatted history. If we connect to a database, this may no longer be necessary.

# Use "communicate_qst" method to obtain a response from gpt for a query.
#   speak = "I am fine"
#   history = [{"text":"Hello", "speaker": "user"}, {"text":"Hello! Are you feeling unwell today?", "speaker":"assistant"}]
#   response = communicate_qst("English", speak, history)
#   newHistory = __create_log(str, response, log)

import connect_gpt

def communicate_qst(lan, speak, log):

    prompt = """
これからあなたは問診を行ってもらいます。
箇条書きされる質問について対話形式で質問を行ってください。
ただし、一度のメッセージでは一言で回答できる質問だけをしてください。その際に括弧の中の選択肢を与えてください。
/の記号で質問を分割して質問を**ひとつだけ**出力してください。
全ての質問が終了したときは、情報をまとめて表示してください。

・具合の悪いところをどこがどのように悪いか
・症状はいつからか
・今までにかかったことのある病気や治療中の病気はあるか（１喘息・２高血圧・３糖尿病・４心臓病・５その他）/それはいつごろか
・今までに手術や輸血の経験はあるか（１ある・２なし）/それはいつ頃か/そのときの病名は何か
・現在服用している薬はあるか（１ある・２なし）/薬の名前は何か
・たばこは吸うか（１吸わない・２吸う・３過去に吸っていた）/１日何本吸っているか/約何年間吸っているか
・アルコールは摂取するか（１飲まない・２飲む）/種類は何か/１回何杯程度飲んでいるか/頻度はどうか（１毎日・２時々・３月２～３回）
"""

    # Creating Chatbot Instances
    qst = connect_gpt.ChatBot(lan, prompt)
    res = qst.speak_to_gpt_with_log(speak, log)

    return res

# Creating formatted log
def __create_log(speak, res, log):

    log.append({"text":speak, "speaker": "user"})
    log.append({"text":res, "speaker":"assistant"})
    
    return log

if __name__ == "__main__":
    log = []

    for i in range(30):
        str = input(">>")
        res = communicate_qst("English", str, log)
        log = __create_log(str, res, log)
