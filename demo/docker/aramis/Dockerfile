FROM python:3.8

RUN pip install -q --upgrade pip && \
    pip install -q supervisor && \
    pip install -q Flask && \
    pip install -q grpcio && \
    pip install -q grpcio-tools && \
    pip install -q bitstruct

RUN apt update && \
    apt install -y libmnl-dev bison flex

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    make && \
    make install

RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-agent-python/clt/ioam-agent.py && \
    wget https://raw.githubusercontent.com/Advanced-Observability/ioam-api/clt/ioam_api.proto

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ioam_api.proto

WORKDIR /apps
COPY supervisord.conf supervisord.conf
COPY app.py app.py

ENTRYPOINT ["/usr/local/bin/supervisord"]
