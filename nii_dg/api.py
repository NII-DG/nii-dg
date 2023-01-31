# type: ignore

from flask import Flask, jsonify, request

from nii_dg.ro_crate import ROCrate

app = Flask(__name__)

# sample


@app.route('/', methods=['GET'])
def hello_world() -> str:
    return "Hello World!"

# Governance function


@app.route('/', methods=['POST'])
def validate():
    # jsonリクエストから値取得
    payload = request.json
    crate_json = payload.get('rocrate')
    crate = ROCrate(from_jsonld=crate_json)
    age = payload.get('age')
    return jsonify({"hoge": "fuga"})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888, debug=True)
