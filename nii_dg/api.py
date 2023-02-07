#!/usr/bin/env python3
# coding: utf-8

import json

from flask import Flask, Response, abort, jsonify, request

from nii_dg.error import GovernanceError
from nii_dg.ro_crate import ROCrate

app = Flask(__name__)


@app.errorhandler(400)
def invalid_crate(e: Exception) -> Response:
    return jsonify(message=str(e)), 400

# sample


@app.route('/', methods=['GET'])
def hello_world() -> str:
    return "Hello World!"

# Governance function


@app.route('/crates', methods=['POST'])
def validate() -> Response:
    # ファイルで送信
    crate_file = request.files.get("ro-crate")
    if crate_file is None:
        # TODO
        raise Exception("need ro-crate-metadata.json as a request body")
    if crate_file.mimetype == "application/json":
        crate_str = crate_file.read().decode()
    else:
        # TODO
        raise Exception("ro-crate MUST be a json file")

    # クエリパラメータ
    # query = request.form
    # hoge = query.get("id")
    crate = ROCrate(from_jsonld=json.loads(crate_str))

    try:
        crate.validate()
        return Response(response=jsonify({"status": "SUCCEEDED"}), status=200)
    except GovernanceError as gov_error:
        return Response(response=jsonify({"status": "FAILED",
                                          "failures": json.loads(str(gov_error))}), status=200)
    except Exception:
        # TODO: 例外クラスを限定する
        abort(400, description="Invalid Crate")


@app.route('/health', methods=['GET'])
def check_health() -> Response:
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
