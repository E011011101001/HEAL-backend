import connect_gpt

def questioner(lan):

    prompt = """
これからあなたは問診を行ってもらいます。
箇条書きされる質問について対話形式で質問を行ってください。
ただし、一度のメッセージでは一言で回答できる質問だけをしてください。その際に括弧の中の選択肢を与えてください。
＋で質問を分割してください
全ての質問が終了したときは、情報をまとめて表示してください

・具合の悪いところをどこがどのように悪いか具体的に
・症状はいつからか
・今までにかかったことのある病気や治療中の病気はあるか（１喘息・２高血圧・３糖尿病・４心臓病・５その他）＋それはいつごろか
・今までに手術や輸血の経験はあるか（１ある・２なし）＋それはいつ頃か＋そのときの病名は何か
・現在服用している薬はあるか（１ある・２なし）＋薬の名前は何か
・たばこは吸うか（１吸わない・２吸う・３過去に吸っていた）＋１日何本・約何年間吸っているか
・アルコールは摂取するか（１飲まない・２飲む）＋種類・１回何杯・頻度（毎日・時々・月２～３回）
"""

    gpt = connect_gpt.ChatBot(lan, prompt)
    return gpt

def communicate_qst(speak, log):

    gpt = questioner("Japanese")
    res = gpt.speak_to_gpt_with_log(speak, log)

    newLog = __create_log(speak, res, log)
    return newLog

def __create_log(speak, res, log):

    log.append({"text":speak, "speaker": "user"})
    log.append({"text":res, "speaker":"assistant"})
    
    return log

if __name__ == "__main__":
    log = []

    for i in range(20):
        str = input(">>")
        log = communicate_qst(str, log)
