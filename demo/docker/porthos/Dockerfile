FROM python:3.8

RUN apt update
RUN apt install -y libmnl-dev bison flex

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    sed -i '/IOAM6_TRACE_DATA_SIZE_MAX 244/i \ __be64 traceId[2]; \ __be64 spanId;' include/uapi/linux/ioam6.h && \
    make && \
    make install

ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]
