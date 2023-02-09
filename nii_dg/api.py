#!/usr/bin/env python3
# coding: utf-8

import json
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, Response, abort, jsonify, request

from nii_dg.error import GovernanceError
from nii_dg.ro_crate import ROCrate

app = Flask(__name__)


def write_to_tmp_file(request_id: str, content: Any) -> None:
    temp_file: Path = Path.cwd()
    temp_file.parent.joinpath(request_id).resolve().mkdir(parents=True, exist_ok=True)
    with temp_file.open(mode="w", encoding="utf-8") as f:
        f.write(str(content))


class CrateValidation(threading.Thread):
    def __init__(self, request_id: str) -> None:
        super().__init__()
        self.request_id = request_id
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        pass
        # try:
        #     for _ in range(1000):
        #         print(f'{datetime.now():%H:%M:%S}')
        #         sleep(1)

        #         # 定期的にフラグを確認して停止させる
        #         if self.stop_event.is_set():
        #             break
        # finally:
        #     print('時間のかかる処理が終わりました\n')


@app.errorhandler(404)
def invalid_crate(e: Exception) -> Response:
    return jsonify(message=str(e)), 404

# Governance function


@app.route('/crates', methods=['POST'])
def post_crates() -> Response:
    crate_file = request.files.get("ro-crate")

    if crate_file is None:
        # TODO
        raise Exception("need ro-crate-metadata.json as a request body")
    if crate_file.mimetype == "application/json":
        crate_str = crate_file.read().decode()
    else:
        # TODO
        raise Exception("ro-crate MUST be a json file")

    request_id = str(uuid4())
    # TODO: id記録してvalidate()実行
    write_to_tmp_file(request_id, "QUEUED")
    t = CrateValidation(request_id)
    t.start()
    return jsonify({"request_id": request_id}), 200

    # # クエリパラメータ
    # # query = request.form
    # # hoge = query.get("id")
    # crate = ROCrate(from_jsonld=json.loads(crate_str))

    # try:
    #     crate.validate()
    #     return Response(response=jsonify({"status": "SUCCEEDED"}), status=200)
    # except GovernanceError as gov_error:
    #     return Response(response=jsonify({"status": "FAILED",
    #                                       "failures": json.loads(str(gov_error))}), status=200)
    # except Exception:
    #     # TODO: 例外クラスを限定する
    #     abort(400, description="Invalid Crate")


@app.route('/health', methods=['GET'])
def check_health() -> Response:
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
