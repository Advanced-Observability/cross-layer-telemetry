FROM python:3 as build

WORKDIR /apps
COPY . .

RUN pip install -q --upgrade pip && \
    pip install -q -r requirements.txt

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile app.py

RUN python -m grpc_tools.protoc -I. --python_out=. \
           --grpc_python_out=. ioam_trace.proto

RUN pyinstaller --log-level CRITICAL --hidden-import pkg_resources.py2_warn --onefile ioam-agent.py

RUN mv ioam.h /usr/include/linux/ && gcc ioam_register.c -o ioam_register

LABEL stage=builder
FROM static-supervisord as base

FROM scratch

EXPOSE 80

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/dist/app /apps/app
COPY --from=build /apps/ioam_register /apps/ioam_register
COPY --from=build /apps/dist/ioam-agent /apps/ioam-agent
COPY --from=build /lib/x86_64-linux-gnu/librt-2.28.so /lib/x86_64-linux-gnu/librt.so.1

ENTRYPOINT ["/usr/bin/supervisord"]
