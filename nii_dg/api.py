# type: ignore

import ast

from flask import Flask, Response, jsonify, request

from nii_dg.error import GovernanceError
from nii_dg.ro_crate import ROCrate

app = Flask(__name__)

# sample


@app.route('/', methods=['GET'])
def hello_world() -> str:
    return "Hello World!"

# Governance function


@app.route('/validate', methods=['POST'])
def validate():
    # jsonリクエストから値取得
    payload = request.json

    # クエリパラメータ
    # query = request.form
    # hoge = query.get("id")
    # ファイルで取得
    # f = request.files["file"]
    # crate_json = json.load(f)
    crate_json = payload.get('rocrate')
    crate = ROCrate(from_jsonld=crate_json)

    try:
        crate.validate()
        return Response(response=jsonify({"status": "SUCCEEDED"}), status=200)
    except GovernanceError as gov_error:
        return Response(response=jsonify({"status": "FAILED",
                                          "failures": ast.literal_eval(str(gov_error))}), status=200)
    except Exception as error:
        return Response(response=jsonify({"status": "ERROR: invalid rocrate",
                                          "error": str(error)}), status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
