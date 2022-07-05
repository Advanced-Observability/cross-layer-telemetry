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
RUN pip install -q Flask==0.12.5
RUN pip install -q opentelemetry-api
RUN pip install -q opentelemetry-sdk
RUN pip install -q opentelemetry-exporter-jaeger-proto-grpc
RUN pip install -q google-api-core
RUN pip install -q google-api-python-client
RUN pip install -q pyroute2
RUN pip install -q requests==2.23.0
RUN pip install -q protobuf==3.20.1
RUN pip install -q Jinja2==3.0.0
RUN pip install -q itsdangerous==2.0.1

WORKDIR /apps
COPY app.py app.py
COPY clt_genl.py clt_genl.py

EXPOSE 15123

ENTRYPOINT ["python"]
CMD ["/apps/app.py"]
