import translator
import highlighter
import questioner

def translate(lan, str, user='PATIENT', errorString="error"):
    """
    translate sentences

    Request:
    lan: string - target language ex. 'en', 'jp', 'French'
    str: string - original text
    user: string - user type
    errorString: string - message when unexpected input

    Response:
    string - translated text
    """

    res = translator.translate(lan, str, user, errorString)
    return res

def extract_medical_term(str, errorString):
    """
    extract medical terms in sentences

    Request:
    str: string - original sentences
    errorString: string - message when unexpected input

    Response:
    string - translated text
    """
    HL = highlighter.highlighter("input language")
    res = HL.search_med_term(str, errorString)

    string_list = res.split(",")
    return string_list

def explain_medical_term(lan, term, errorString):
    """
    explain medical term

    Request:
    lan: string - target language ex. 'en', 'jp', 'French'
    term: string - a medical term
    errorString: string - message when unexpected input

    Response:
    {
        "exp": "covid-19 is ___",
        "link": "https://___"
    }
    """
    HL = highlighter.highlighter(lan)
    res = HL.search_med_term(term, errorString)

    return res

def questioner_chat(lan, str, log):
    """
    explain medical term

    Request:
    lan: string - target language ex. 'en', 'jp', 'French'
    str: string - last text patient input
    log: string[] - message history

    Response:
    string - response text by chat bot
    """

    Qst = questioner.AIDoctor(lan, log)
    res = Qst.send_and_get_reply(str)

    return res
