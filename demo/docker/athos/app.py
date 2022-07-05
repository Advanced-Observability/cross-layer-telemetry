import time
import json
import socket

from flask import Flask, Response, request
from http.client import HTTPConnection
from requests.packages import urllib3
from werkzeug.serving import WSGIRequestHandler
from clt_genl import CrossLayerTelemetry

from opentelemetry import trace
from opentelemetry.exporter.jaeger.proto.grpc import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MyHTTPConnection(HTTPConnection):
    open_socket = None

    def connect(self):
        self.sock = self.open_socket

urllib3.connectionpool.HTTPConnection = MyHTTPConnection
urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = MyHTTPConnection
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def trace_request(web_path, clt, http, tracer, span_name):
    data = {
        'username': request.form.get('username'), 
        'password': request.form.get('password'),
    }

    body = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}

    span = tracer.start_span(span_name)

    sock = MyHTTPConnection.open_socket
    clt.enable(sock.fileno(), span.context.trace_id, span.context.span_id)

    # START MONITORING
    span._start_time = int(time.time() * 1e9)
    http.request('POST', web_path, body, headers)
    res = http.getresponse().read()
    span.end()
    # END MONITORING

    clt.disable(sock.fileno())
    return res


app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    res = trace_request('/login', clt, http, tracer, 'login')

    output = "<html><head><title>CLT demo - Login API</title></head><body>"
    output += "<h3>Login API</h3>"
    output += "<p>Response from the server: <b>"+ json.loads(res)['msg'] +"</b></p>"
    output += "<p>Admin section: \
               <a href='http://localhost:16686' target='_blank'>Jaeger UI</a></p>"
    output += "<a href='javascript:history.back()'>Go Back</a>"
    output += "</body></html>"

    return Response(output, status=200, mimetype='text/html')


if __name__ == '__main__':
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "CLT-demo"})
        )
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(insecure=True)
        )
    )

    tracer = trace.get_tracer(__name__)

    time.sleep(3)

    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.connect(('db02::2', 80))

    MyHTTPConnection.open_socket = sock
    http = MyHTTPConnection("["+ str(sock.getpeername()[0]) +"]")

    clt = CrossLayerTelemetry()

    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host='0.0.0.0', port=15123)

