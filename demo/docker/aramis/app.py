import json
from flask import Flask, Response, jsonify, request
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
	data = json.loads(request.data.decode("utf-8"))
	if data.get('username') == "clt" and data.get('password') == "clt":
		return jsonify(msg='OK')

	return jsonify(msg='FAILED')

if __name__ == '__main__':
	WSGIRequestHandler.protocol_version = "HTTP/1.1"
	app.run(host='::', port=80)
