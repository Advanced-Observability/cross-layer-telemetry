FROM python:3.8 as build
LABEL stage=builder

WORKDIR /apps
COPY app.py app.py
COPY clt_genl.py clt_genl.py
COPY supervisord.conf supervisord.conf

RUN pip install -q --upgrade pip && \
    pip install -q Flask==0.12.5 && \
    pip install -q requests==2.23.0 && \
    pip install -q jaeger-client==4.3.0 && \
    pip install -q pyinstaller==3.6 && \
    pip install -q pyroute2==0.5.17

RUN apt update && apt install -y libmnl-dev bison flex
RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.10.0.tar.xz && tar -Jxvf iproute2-5.10.0.tar.xz && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%231.patch && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%232.patch && wget https://raw.githubusercontent.com/IurmanJ/cross-layer-telemetry/master/CLT.patch && cd iproute2-5.10.0 && patch -p1 < ../#1.patch && patch -p1 < ../#2.patch && (patch -p1 --forward < ../CLT.patch || true) && make && make install

RUN sed -i 's/jaeger./jaeger_client.thrift_gen.jaeger./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/ttypes.py 
RUN sed -i 's/jaeger./jaeger_client.thrift_gen.jaeger./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/Agent.py 
RUN sed -i 's/zipkincore./jaeger_client.thrift_gen.zipkincore./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/ttypes.py
RUN sed -i 's/zipkincore./jaeger_client.thrift_gen.zipkincore./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/Agent.py

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile app.py

FROM static-supervisord as base
LABEL stage=builder

FROM jaegertracing/jaeger-agent:1.18 as agent
LABEL stage=builder

FROM scratch

EXPOSE 5775/udp 5778 6831/udp 6832/udp 14271 15123

COPY --from=agent /go/bin/agent-linux /go/bin/agent-linux

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/dist/app /apps/app
COPY --from=build /sbin/ip /sbin/ip
COPY --from=build /lib/x86_64-linux-gnu/libnss_files-2.28.so /lib/x86_64-linux-gnu/libnss_files.so.2
COPY --from=build /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libselinux.so.1
COPY --from=build /lib/x86_64-linux-gnu/libmnl.so.0.2.0 /lib/x86_64-linux-gnu/libmnl.so.0
COPY --from=build /lib/x86_64-linux-gnu/libdl-2.28.so /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /lib/x86_64-linux-gnu/libz.so.1.2.11 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=build /lib/x86_64-linux-gnu/libc-2.28.so /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libpcre.so.3.13.3 /lib/x86_64-linux-gnu/libpcre.so.3
COPY --from=build /lib/x86_64-linux-gnu/libpthread-2.28.so /lib/x86_64-linux-gnu/libpthread.so.0

ENTRYPOINT ["/usr/bin/supervisord"]

