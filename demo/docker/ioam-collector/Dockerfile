FROM golang:1.15-alpine

RUN apk add git

# Install OpenTelemetry's Jaeger exporter
RUN go get -u go.opentelemetry.io/otel/exporters/jaeger

# Install Protobuf and gRPC for Golang
RUN apk add protobuf protobuf-dev && \
    go get github.com/golang/protobuf/protoc-gen-go && \
    go get google.golang.org/grpc

WORKDIR /apps
#TODO remove copy, wget directly from this repo
COPY ioam-collector.go ioam-collector.go

#TODO replace
#RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-api/clt/ioam_api.proto
COPY ioam_api.proto ioam_api.proto

# Build IOAM collector
RUN mkdir $GOPATH/src/ioam && \
    protoc --go_out=plugins=grpc:$GOPATH/src/ioam ioam_api.proto

RUN CGO_ENABLED=0 go build ioam-collector.go

ENTRYPOINT ["/apps/ioam-collector"]
