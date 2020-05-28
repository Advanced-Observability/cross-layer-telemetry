FROM python:3 as build

WORKDIR /apps
COPY . .

RUN pip install -q --upgrade pip && \
    pip install -q -r requirements.txt

RUN sed -i 's/jaeger./jaeger_client.thrift_gen.jaeger./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/ttypes.py 
RUN sed -i 's/jaeger./jaeger_client.thrift_gen.jaeger./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/Agent.py 
RUN sed -i 's/zipkincore./jaeger_client.thrift_gen.zipkincore./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/ttypes.py
RUN sed -i 's/zipkincore./jaeger_client.thrift_gen.zipkincore./g' /usr/local/lib/python3.8/site-packages/jaeger_client/thrift_gen/agent/Agent.py

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile app.py

RUN mv ioam.h /usr/include/linux/ && gcc ioam_register.c -o ioam_register

LABEL stage=builder
FROM static-supervisord as base
FROM jaegertracing/jaeger-agent:latest as agent

FROM scratch

EXPOSE 5775/udp 5778 6831/udp 6832/udp 14271 15123

COPY --from=agent /go/bin/agent-linux /go/bin/agent-linux

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/dist/app /apps/app
COPY --from=build /apps/ioam_register /apps/ioam_register
COPY --from=build /lib/x86_64-linux-gnu/libnss_files-2.28.so /lib/x86_64-linux-gnu/libnss_files.so.2

ENTRYPOINT ["/usr/bin/supervisord"]
