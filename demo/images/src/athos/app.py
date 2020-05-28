import time
import logging
import socket
import ctypes
import json
from flask import Flask, Response
from jaeger_client import Config
from http.client import HTTPConnection
from requests.packages import urllib3
from werkzeug.serving import WSGIRequestHandler

syscall_num = 333

libc = ctypes.CDLL(None)
_ioam_syscall = libc.syscall
_ioam_syscall.restypes = ctypes.c_int
_ioam_syscall.argtypes = ctypes.c_int, ctypes.c_int, ctypes.c_uint64, \
			 ctypes.c_uint64, ctypes.c_uint64

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MyHTTPConnection(HTTPConnection):
	open_socket = None

	def connect(self):
		self.sock = self.open_socket

urllib3.connectionpool.HTTPConnection = MyHTTPConnection
urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = MyHTTPConnection
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def trace_request(sock, method, web_path, tracer, span_name):
	span = tracer.start_span(span_name)

	trace_id_high = span.trace_id >> 64
	trace_id_low  = span.trace_id & 0x0000000000000000ffffffffffffffff

	ioam_sockfd = _ioam_syscall(syscall_num, sock.fileno(), trace_id_high,
				    trace_id_low, span.span_id)
	ioam_sock = socket.socket(fileno=ioam_sockfd)

	MyHTTPConnection.open_socket = ioam_sock
	c = MyHTTPConnection("["+ str(sock.getpeername()[0]) +"]")

	span.start_time = time.time()
	c.request(method, web_path)
	span.finish()

	res = c.getresponse().read()

	c.close()
	return res

app = Flask(__name__)

@app.route('/api/request')
def request():
	tracer = config.new_tracer()

	sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	sock.connect(('db02::2', 80))

	r1 = trace_request(sock, 'GET', '/check', tracer, 'span_check')
	r2 = trace_request(sock, 'GET', '/validate', tracer, 'span_validate')

	time.sleep(2)
	sock.close()
	tracer.close()

	output = "<html><head><title>CLT demo</title></head><body>"
	output += "<h2>Welcome to the Cross-Layer Telemetry demo !</h2>"
	output += "<p>Your HTTP request to <b><i>/api/request</i></b> just \
		   generated two sub-requests in brackground to a local server"
	output += "<ul>"
	output += "<li>sub-request to <b><i>/check</i></b></li>"
	output += "<li>sub-request to <b><i>/validate</i></b></li>"
	output += "</ul>"
	output += "where each sub-request randomly inserts a delay between 0 \
		   and 1 second.</p>"
	output += "<p>Responses from the server for each sub-request:"
	output += "<ul>"
	output += "<li>"+ json.loads(r1)['msg'] +"</li>"
	output += "<li>"+ json.loads(r2)['msg'] +"</li>"
	output += "</ul></p>"
	output += "<p>Now, let's visualize the result \
		   <a href='http://localhost:16686'>in Jaeger UI</a></p>"
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
		service_name='API Request',
		validate=True,
	)

	WSGIRequestHandler.protocol_version = "HTTP/1.1"
	app.run(host='0.0.0.0', port=15123)
