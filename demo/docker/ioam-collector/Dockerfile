FROM golang:1.14-alpine

RUN go get -u go.opentelemetry.io/otel/exporters/jaeger

WORKDIR /apps
#TODO remove copy and directly wget ioam-collector.go as soon as the repo is updated
COPY ioam-collector.go ioam-collector.go

ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]
