FROM python:3 as build

WORKDIR /tmp
COPY supervisor.patch supervisor.patch

RUN pip install -q --upgrade pip && \
    pip install -q pyinstaller==3.6

RUN wget -q https://github.com/Supervisor/supervisor/archive/4.2.0.tar.gz && \
    tar zxf 4.2.0.tar.gz && \
    cd supervisor-4.2.0 && \
    patch -p1 < ../supervisor.patch

RUN pyinstaller --log-level CRITICAL \
                --hidden-import pkg_resources.py2_warn \
                --onefile supervisor-4.2.0/supervisor/supervisord.py

RUN mv dist/supervisord /usr/bin/supervisord && \
    rm -rf *

LABEL stage=builder
FROM scratch

COPY --from=build /tmp /tmp
COPY --from=build /usr/bin/supervisord /usr/bin/supervisord
COPY --from=build /lib/x86_64-linux-gnu/libdl-2.28.so /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /lib/x86_64-linux-gnu/libz.so.1.2.11 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=build /lib/x86_64-linux-gnu/libc-2.28.so /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/ld-2.28.so /lib64/ld-linux-x86-64.so.2
COPY --from=build /lib/x86_64-linux-gnu/libcrypt.so.1 /lib/x86_64-linux-gnu/libcrypt.so.1
COPY --from=build /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0
COPY --from=build /lib/x86_64-linux-gnu/libutil.so.1 /lib/x86_64-linux-gnu/libutil.so.1
COPY --from=build /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6
