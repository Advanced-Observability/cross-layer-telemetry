FROM python:3.8 as build
LABEL stage=builder

WORKDIR /apps
COPY app.py app.py
COPY supervisord.conf supervisord.conf

RUN pip install -q --upgrade pip && \
    pip install -q Flask==0.12.5 && \
    pip install -q grpcio==1.28.1 && \
    pip install -q grpcio-tools==1.28.1 && \
    pip install -q bitstruct==8.10.0 && \
    pip install -q pyinstaller==3.6

RUN apt update && apt install -y libmnl-dev bison flex
RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.10.0.tar.xz && tar -Jxvf iproute2-5.10.0.tar.xz && wget https://raw.githubusercontent.com/IurmanJ/ioam-agent/clt/ioam-agent.py && wget https://raw.githubusercontent.com/IurmanJ/ioam-proto3/main/ioam_trace.proto && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%231.patch && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%232.patch && wget https://raw.githubusercontent.com/IurmanJ/cross-layer-telemetry/master/CLT.patch && cd iproute2-5.10.0 && patch -p1 < ../#1.patch && patch -p1 < ../#2.patch && (patch -p1 --forward < ../CLT.patch || true) && make && make install

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile app.py

RUN python -m grpc_tools.protoc -I. --python_out=. \
           --grpc_python_out=. ioam_trace.proto

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile ioam-agent.py

FROM static-supervisord as base
LABEL stage=builder

FROM scratch

EXPOSE 80

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/dist/app /apps/app
COPY --from=build /apps/dist/ioam-agent /apps/ioam-agent
COPY --from=build /sbin/ip /sbin/ip
COPY --from=build /lib/x86_64-linux-gnu/librt-2.28.so /lib/x86_64-linux-gnu/librt.so.1
COPY --from=build /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libselinux.so.1
COPY --from=build /lib/x86_64-linux-gnu/libmnl.so.0.2.0 /lib/x86_64-linux-gnu/libmnl.so.0
COPY --from=build /lib/x86_64-linux-gnu/libdl-2.28.so /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /lib/x86_64-linux-gnu/libc-2.28.so /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libpcre.so.3.13.3 /lib/x86_64-linux-gnu/libpcre.so.3
COPY --from=build /lib/x86_64-linux-gnu/libpthread-2.28.so /lib/x86_64-linux-gnu/libpthread.so.0

ENTRYPOINT ["/usr/bin/supervisord"]

