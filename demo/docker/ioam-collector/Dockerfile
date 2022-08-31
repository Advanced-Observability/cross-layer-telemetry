FROM golang:1.19-alpine

RUN apk add protobuf protobuf-dev
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

WORKDIR /apps

# Build IOAM API for gRPC
RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-api/clt/ioam_api.proto
RUN protoc --go_out=. --go-grpc_out=. ioam_api.proto

# Build IOAM collector
RUN wget https://raw.githubusercontent.com/Advanced-Observability/ioam-collector-go-jaeger/main/ioam-collector.go
RUN go mod init ioam-collector
RUN go mod tidy
RUN CGO_ENABLED=0 go build ioam-collector.go

ENTRYPOINT ["/apps/ioam-collector"]
