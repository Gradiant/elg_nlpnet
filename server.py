from typing import re

from flask import Flask, request
from flask_json import FlaskJSON, JsonError
import nlpnet
from nlpnet.taggers import SRLAnnotatedSentence

app = Flask(__name__)
# Don't add an extra "status" property to JSON responses - this would break the API contract
app.config["JSON_ADD_STATUS"] = False
# Don't sort properties alphabetically in response JSON
app.config["JSON_SORT_KEYS"] = False

json_app = FlaskJSON(app)


def error_response(code, text):
    raise JsonError(
        status_=400, failure={"errors": [{"code": str(code), "text": str(text)}]}
    )


def generate_successful_response(text, method):
    response = []

    if method == "pos":
        for item in text[0]:
            response.append({"content": item[0], "role": item[1]})
    else:
        result = text[0][1]

        for i in result.items():
            texts = []
            for j in i[1]:
                texts.append({"content": j})
            response.append({"role": i[0], "texts": texts})

    print(response)

    return {"response": {"type": "texts", "texts": response}}


def generate_failure_response(status, code, text, params, detail):
    error = {}
    if code:
        error["code"] = code
    if text:
        error["text"] = text
    if params:
        error["params"] = params
    if detail:
        error["detail"] = {"message": str(detail)}

    raise JsonError(status_=status, failure={"errors": [error]})


# Scripts
@app.route("/tag_process", methods=["POST"])
def tag_process():
    data = request.get_json()

    if data["type"] != "text":
        return generate_failure_response(
            status=400,
            code="elg.request.type.unsupported",
            text="Request type {0} not supported by this service",
            params=[data["type"]],
            detail=None,
        )
    if "content" not in data:
        return invalid_request_error(None, "Content parameter not in request")

    content = data.get("content")
    params = data.get("params", {})
    if "task" not in params:
        return invalid_request_error(None, "task parameter not in request")

    if params["task"] not in ["srl", "pos"]:
        return invalid_request_error(None, "task should be 'srl' or 'pos'")

    # Params
    v = ""
    gold = ""
    t = ""
    norepeat = ""
    lang = "pt"  # pt for defect
    method = params["task"]

    if "v" in params:
        v = params["v"]
    if "gold" in params:
        gold = params["gold"]
    if "lang" in params:
        lang = params["lang"]
    if "t" in params:
        t = params["t"]
    if "norepeat" in params:
        norepeat = params["norepeat"]

    if lang != "pt":
        return invalid_request_error(
            None, "Only language supported is portuguese ('pt')"
        )

    try:
        result = run_tagger(method, v, t, lang, norepeat, gold, content)
    except Exception as e:
        text = "Unexpected error."
        # Standard message for internal error - the real error message goes in params
        return generate_failure_response(
            status=500,
            code="elg.service.internalError",
            text="Internal error during processing: {0}",
            params=[text],
            detail=None,
        )
    return generate_successful_response(result, method)


def run_tagger(method, v, t, lang, norepeat, gold, text):
    data = "models/" + method + "-" + lang
    nlpnet.set_data_dir(data)

    if method == "srl":
        tagger = nlpnet.SRLTagger(language=lang)
        tag = tagger.tag(text)
        sent = tag[0].arg_structures
    else:
        tagger = nlpnet.POSTagger(language=lang)
        sent = tagger.tag(text)

    return sent


@json_app.invalid_json_error
def invalid_request_error(e, message):
    """Generates a valid ELG "failure" response if the request cannot be parsed"""
    raise JsonError(
        status_=400,
        failure={
            "errors": [
                {
                    "code": "elg.request.invalid",
                    "text": "Invalid request message: " + message,
                }
            ]
        },
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8866)
