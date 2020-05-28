FROM python:3 as build

WORKDIR /apps
COPY . .

RUN mv ioam.h /usr/include/linux/ && gcc ioam_register.c -o ioam_register

LABEL stage=builder
FROM static-supervisord as base

FROM scratch

COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /tmp /tmp
COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/ioam_register /apps/ioam_register

ENTRYPOINT ["/usr/bin/supervisord"]
