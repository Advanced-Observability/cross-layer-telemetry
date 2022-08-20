FROM python:3.8

RUN apt update --fix-missing
RUN apt install -y libmnl-dev bison flex tcpdump

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    sed -i '/IOAM6_TRACE_DATA_SIZE_MAX 244/i \ struct { \ __be64 high, low; \ } pkt_id; \ __be64 pkt_sid;' include/uapi/linux/ioam6.h && \
    make && \
    make install

RUN pip install -q --upgrade pip
RUN pip install -q supervisor

WORKDIR /apps
COPY supervisord.conf supervisord.conf

ENTRYPOINT ["/usr/local/bin/supervisord"]
