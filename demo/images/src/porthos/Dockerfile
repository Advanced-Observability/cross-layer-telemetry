FROM python:3.8 as build
LABEL stage=builder

WORKDIR /apps
COPY empty.c empty.c
COPY supervisord.conf supervisord.conf

RUN gcc empty.c -o empty

RUN apt update && apt install -y libmnl-dev bison flex
RUN wget https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/iproute2-5.10.0.tar.xz && tar -Jxvf iproute2-5.10.0.tar.xz && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%231.patch && wget https://raw.githubusercontent.com/IurmanJ/kernel_ipv6_ioam/master/iproute2/%232.patch && wget https://raw.githubusercontent.com/IurmanJ/cross-layer-telemetry/master/CLT.patch && cd iproute2-5.10.0 && patch -p1 < ../#1.patch && patch -p1 < ../#2.patch && (patch -p1 --forward < ../CLT.patch || true) && make && make install

FROM static-supervisord as base
LABEL stage=builder

FROM scratch

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /sbin/ip /sbin/ip
COPY --from=build /sbin/tc /sbin/tc
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/empty /apps/empty

COPY --from=build /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libselinux.so.1
COPY --from=build /usr/lib/x86_64-linux-gnu/libelf-0.176.so /usr/lib/x86_64-linux-gnu/libelf.so.1
COPY --from=build /lib/x86_64-linux-gnu/libmnl.so.0.2.0 /lib/x86_64-linux-gnu/libmnl.so.0
COPY --from=build /lib/x86_64-linux-gnu/libm-2.28.so /lib/x86_64-linux-gnu/libm.so.6
COPY --from=build /lib/x86_64-linux-gnu/libdl-2.28.so /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /usr/lib/x86_64-linux-gnu/libxtables.so.12.2.0 /usr/lib/x86_64-linux-gnu/libxtables.so.12
COPY --from=build /lib/x86_64-linux-gnu/libc-2.28.so /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libpcre.so.3.13.3 /lib/x86_64-linux-gnu/libpcre.so.3
COPY --from=build /lib/x86_64-linux-gnu/libz.so.1.2.11 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=build /lib/x86_64-linux-gnu/libpthread-2.28.so /lib/x86_64-linux-gnu/libpthread.so.0

ENTRYPOINT ["/usr/bin/supervisord"]
