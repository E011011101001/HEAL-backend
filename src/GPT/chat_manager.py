from . import highlighter

def extract_medical_term(lan_code, text) -> list[dict]:
    """
    extract medical terms in sentences

    Request:
    str: string - original sentences
    errorString: string - message when unexpected input

    Response:
    [
        {
            "term": "Covid19",
            "synonyms": ["Covid19", "covid-19"]
        },
        {
            "term": "inhalar",
            "synonyms": ["inhalar"]
        }
    ]
    """
    termDictList = []
    terms = highlighter.search_med_term(lan_code, text)

    for term in terms:
        synonyms = highlighter.get_synonym(lan_code, term)
        synonyms.append(term)

        termDictList.append({"term": term, "synonyms": synonyms})

    return termDictList

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
