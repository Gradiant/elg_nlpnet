from typing import re

from flask import Flask, request
from flask_json import FlaskJSON, JsonError
import nlpnet
from nlpnet.taggers import SRLAnnotatedSentence

app = Flask(__name__)
# Don't add an extra "status" property to JSON responses - this would break the API contract
app.config['JSON_ADD_STATUS'] = False
# Don't sort properties alphabetically in response JSON
app.config['JSON_SORT_KEYS'] = False

json_app = FlaskJSON(app)


def error_response(code, text):
    raise JsonError(status_=400, failure={'errors': [
        {'code': str(code), 'text': str(text)}
    ]})


def generate_successful_response(text, method):
    response = []

    if method == "pos":
        for item in text[0]:
            response.append({'content': item[0], 'role': item[1]})
    else:
        result = text[0][1]

        for i in result.items():
            texts = []
            for j in i[1]:
                texts.append({'content': j})
            response.append({'role': i[0], 'texts': texts})

    print(response)

    return {"response": {"type": "texts", "texts": response}}


def generate_failure_response(status, code, text, params, detail):
    error = {}
    if code: error["code"] = code
    if text: error["text"] = text
    if params: error["params"] = params
    if detail: error["detail"] = {"message": detail}

    raise JsonError(status_=status, failure={'errors': [error]})


# Scripts
@app.route("/tag_process", methods=['POST'])
def tag_process():
    data = request.get_json()
    print(data)
    # Error check in requests
    if 'content' not in data:
        return error_response(code="elg.request.invalid", text="Error in input text.")
    elif 'task' not in data['params']:
        return error_response(code="elg.request.invalid", text="Invalid method.")
    elif data['params']['task'] != 'srl' and data['params']['task'] != 'pos':
        return error_response(code="elg.request.invalid", text="Invalid method.")

    # Params
    v = ''
    gold = ''
    t = ''
    norepeat = ''
    lang = 'pt'  # pt for defect
    params = data['params']
    method = params['task']

    if 'v' in params:
        v = params['v']
    if 'gold' in params:
        gold = params['gold']
    if 'lang' in params:
        lang = params['lang']
    if 't' in params:
        t = params['t']
    if 'norepeat' in params:
        norepeat = params['norepeat']

    # Text
    text = data['content']
    print(text)
    try:
        result = run_tagger(method, v, t, lang, norepeat, gold, text)
    except Exception as e:
        return generate_failure_response(status=404, code="elg.service.internalError", text=None, params=None,
                                         detail=str(e))
    return generate_successful_response(result, method)


def run_tagger(method, v, t, lang, norepeat, gold, text):
    data = 'models/' + method + '-' + lang
    nlpnet.set_data_dir(data)

    if method == "srl":
        tagger = nlpnet.SRLTagger(language=lang)
        tag = tagger.tag(text)
        sent = tag[0].arg_structures
    else:
        tagger = nlpnet.POSTagger(language=lang)
        sent = tagger.tag(text)

    return sent


if __name__ == '__main__':
    app.run(host="0.0.0.0")
