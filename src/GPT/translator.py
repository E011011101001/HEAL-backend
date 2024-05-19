# src/GPT/translator.py
import json

from . import ChatBot
from ..utils import print_info


translators = {}


def translate_to(lan_code: str, text: str):
    translator = translators.get(lan_code)
    prompt = f"""You are a translator API and you speak in JSON. Please recognize the input language and translate it
into the language specified by the language code {lan_code}. Normally, The format of your output content should be
{'status': 'OK', 'translation': 'This is a translated sentence'}
Please only output the JSON and no more, because your output will be passed directly to a JSON-to-Python-dict parser.

Here is some context explanation that might help you translate better. The conversation happens on an online
interrogation platform between doctors and patients. They speak different language and that is what you are helping
with. Please translate accurately and professionally.

There might be some unexpected input. When that happens, change the JSON attribute 'status' to 'error' and put the
reason in 'reason', like
{'status': 'error', 'reason': 'Input language and the translation target language are the same.'}
or
{'status': 'error', 'reason': 'Not a sentence.'}
    """
    if translator is None:
        translators[lan_code] = ChatBot(lan_code, prompt)
        translator = translators[lan_code]

    output = json.load(translator.chat(text))

    if output.get('status') == 'OK':
        return output.get('translation')

    # error
    print_info(output)
    return ''
