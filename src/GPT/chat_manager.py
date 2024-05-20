from . import highlighter

def extract_medical_term(lan_code, text) -> list[dict]:
    """
    extract medical terms in sentences

    Request:
    lan_code: string
    text: string - original sentences

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

def explain_medical_term(lan_code, term):
    """
    explain medical term

    Request:
    lan_code: string
    term: string - a medical term

    Response:
    {
        "type": "CONDITION"
        "description": "covid-19 is ___",
        "url": "https://___"
    }
    """
    termType = highlighter.get_termType(lan_code, term)
    termDescription = highlighter.explain_med_term(lan_code, term)
    termUrl = highlighter.get_url(lan_code, term)

    res = {
        "type": termType,
        "description": termDescription,
        "url": termUrl
    }

    return res
