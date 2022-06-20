FROM python:3.8

RUN apt update && \
    apt install -y libmnl-dev bison flex

RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.17.0.tar.xz && \
    tar -Jxvf iproute2-5.17.0.tar.xz && \
    cd iproute2-5.17.0 && \
    make && \
    make install

ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]
