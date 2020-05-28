import time
import random
from flask import Flask, Response, jsonify
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)

@app.route('/check')
def check():
	x = random.random()
	time.sleep(x)

	data = 'The API sub-request to <b><i>/check</i></b> was successful \
		(took '+ str(x) +' second)'

	return jsonify(msg=data)

@app.route('/validate')
def validate():
	x = random.random()
	time.sleep(x)

	data = 'The API sub-request to <b><i>/validate</i></b> was successful \
		(took '+ str(x) +' second)'

	return jsonify(msg=data)

if __name__ == '__main__':
	WSGIRequestHandler.protocol_version = "HTTP/1.1"
	app.run(host='::', port=80)
