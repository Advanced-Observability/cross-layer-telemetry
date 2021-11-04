FROM golang:1.14-alpine as build
LABEL stage=builder

WORKDIR /apps
COPY ioam-collector.go ioam-collector.go
COPY supervisord.conf supervisord.conf

RUN wget https://raw.githubusercontent.com/IurmanJ/ioam-proto3/main/ioam_trace.proto

# Install jaeger-client for Golang
RUN apk add curl dep make git && \
    go get -u github.com/uber/jaeger-client-go && \
    cd $GOPATH/src/github.com/uber/jaeger-client-go/ && \
    git submodule update --init --recursive && \
    make install

# Install Protobuf and gRPC for Golang
RUN apk add protobuf protobuf-dev && \
    go get github.com/golang/protobuf/protoc-gen-go && \
    go get google.golang.org/grpc

# Build IOAM collector
RUN mkdir $GOPATH/src/ioam && \
    protoc --go_out=plugins=grpc:$GOPATH/src/ioam ioam_trace.proto && \
    CGO_ENABLED=0 go build ioam-collector.go

FROM static-supervisord as base
LABEL stage=builder

FROM jaegertracing/jaeger-agent:1.18 as agent
LABEL stage=builder

FROM scratch

EXPOSE 5775/udp 5778 6831/udp 6832/udp 7123 14271

COPY --from=agent /go/bin/agent-linux /go/bin/agent-linux

COPY --from=base /tmp /tmp
COPY --from=base /lib /lib
COPY --from=base /lib64 /lib64
COPY --from=base /usr/bin/supervisord /usr/bin/supervisord

COPY --from=build /apps/supervisord.conf /etc/supervisord.conf
COPY --from=build /apps/ioam-collector /apps/ioam-collector

ENTRYPOINT ["/usr/bin/supervisord"]
