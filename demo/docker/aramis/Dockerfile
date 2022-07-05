FROM python:3.8

RUN apt update
RUN apt install -y libmnl-dev bison flex

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    sed -i '/IOAM6_TRACE_DATA_SIZE_MAX 244/i \ __be64 traceId[2]; \ __be64 spanId;' include/uapi/linux/ioam6.h && \
    make && \
    make install

RUN pip install -q --upgrade pip
RUN pip install -q supervisor
RUN pip install -q Flask==0.12.5
RUN pip install -q grpcio
RUN pip install -q grpcio-tools
RUN pip install -q bitstruct
RUN pip install -q Jinja2==3.0.0
RUN pip install -q itsdangerous==2.0.1

WORKDIR /apps
COPY app.py app.py
COPY supervisord.conf supervisord.conf

RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-agent-python/clt/ioam-agent.py
RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-api/clt/ioam_api.proto

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ioam_api.proto

ENTRYPOINT ["/usr/local/bin/supervisord"]
