import time
import json
import socket
import logging
from flask import Flask, Response, request
from jaeger_client import Config
from http.client import HTTPConnection
from requests.packages import urllib3
from werkzeug.serving import WSGIRequestHandler
from clt_genl import CrossLayerTelemetry

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MyHTTPConnection(HTTPConnection):
	open_socket = None

	def connect(self):
		self.sock = self.open_socket

urllib3.connectionpool.HTTPConnection = MyHTTPConnection
urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = MyHTTPConnection
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def trace_request(web_path, clt, http, tracer, span_name):
	span = tracer.start_span(span_name)

	sock = MyHTTPConnection.open_socket
	clt.enable(sock.fileno(), span.trace_id, span.span_id)

	data = {'username': request.form.get('username'), 
		'password': request.form.get('password')}

	body = json.dumps(data).encode('utf-8')
	headers = {'Content-Type': 'application/json'}

	# START MONITORING
	span.start_time = time.time()
	http.request('POST', web_path, body, headers)
	res = http.getresponse().read()
	span.finish()
	# END MONITORING

	clt.disable(sock.fileno())
	return res

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def api_login():
	res = trace_request('/login', clt, http, tracer, 'span_login')

	output = "<html><head><title>CLT demo - Login API</title></head><body>"
	output += "<h3>Login API</h3>"
	output += "<p>Response from the server: <b>"+ json.loads(res)['msg'] +"</b></p>"
	output += "<p>Admin section: \
		   <a href='http://localhost:16686' target='_blank'>Jaeger UI</a></p>"
	output += "<a href='javascript:history.back()'>Go Back</a>"
	output += "</body></html>"

	return Response(output, status=200, mimetype='text/html')

if __name__ == '__main__':
	log_level = logging.DEBUG
	logging.getLogger('').handlers = []
	logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

	config = Config(
		config={
			'sampler': {
				'type': 'const',
				'param': 1,
			},
			'logging': True,
		},
		service_name='Login API',
		validate=True,
	)
	tracer = config.new_tracer()

	sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	sock.connect(('db02::2', 80))

	MyHTTPConnection.open_socket = sock
	http = MyHTTPConnection("["+ str(sock.getpeername()[0]) +"]")

	clt = CrossLayerTelemetry()

	WSGIRequestHandler.protocol_version = "HTTP/1.1"
	app.run(host='0.0.0.0', port=15123)

