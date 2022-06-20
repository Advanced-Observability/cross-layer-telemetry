FROM python:3.8

RUN pip install -q --upgrade pip && \
    pip install -q Flask && \
    pip install -q opentelemetry-api && \
    pip install -q opentelemetry-sdk && \
    pip install -q opentelemetry-exporter-jaeger-proto-grpc && \
    pip install -q google-api-core && \
    pip install -q google-api-python-client

RUN apt update && \
    apt install -y libmnl-dev bison flex

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    make && \
    make install

WORKDIR /apps
COPY app.py app.py

EXPOSE 15123

ENTRYPOINT ["python"]
CMD ["/apps/app.py"]
#ENTRYPOINT ["/bin/bash","-c"]
