package main

import (
	"encoding/hex"
	"log"
	"net"
	"strconv"

	"ioam"
	empty "github.com/golang/protobuf/ptypes/empty"
	"golang.org/x/net/context"
	"google.golang.org/grpc"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/trace"
	tracesdk "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.10.0"
)

const (
	service     = "CLT-demo"
	environment = "production"
	id          = 1
)

var HAS_HOPLIMIT		= uint32(1 << 31)
var HAS_ID			= uint32(1 << 30)
var HAS_INGRESSID		= uint32(1 << 29)
var HAS_EGRESSID		= uint32(1 << 28)
var HAS_TIMESTAMPSECS		= uint32(1 << 27)
var HAS_TIMESTAMPFRAC		= uint32(1 << 26)
var HAS_TRANSITDELAY		= uint32(1 << 25)
var HAS_QUEUEDEPTH		= uint32(1 << 24)
var HAS_CSUMCOMP		= uint32(1 << 23)
var HAS_BUFFEROCCUPANCY	= uint32(1 << 22)
var HAS_INGRESSIDWIDE		= uint32(1 << 21)
var HAS_EGRESSIDWIDE		= uint32(1 << 20)
var HAS_IDWIDE			= uint32(1 << 19)
var HAS_NAMESPACEDATA		= uint32(1 << 18)
var HAS_NAMESPACEDATAWIDE	= uint32(1 << 17)
var HAS_OSS			= uint32(1 << 16)

func main() {
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint())
	if err != nil {
		log.Fatal(err)
	}
	tp := tracesdk.NewTracerProvider(
		tracesdk.WithBatcher(exp),
		tracesdk.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceNameKey.String(service),
			attribute.String("environment", environment),
			attribute.Int64("ID", id),
		)),
	)
	otel.SetTracerProvider(tp)

	grpcServer := grpc.NewServer()
	var server Server
	ioam_api.RegisterIOAMServiceServer(grpcServer, server)
	listen, err := net.Listen("tcp", ":7123")
	if err != nil {
		log.Fatalf("could not listen: %v", err)
	}

	log.Println("IOAM collector starting...")
	log.Fatal(grpcServer.Serve(listen))
}

type Server struct{}

func (Server) Report(grpc_ctx context.Context, request *ioam_api.IOAMTrace) (*empty.Empty, error) {
	log.Println("receiving IOAM data from the agent...")

	span_ctx := trace.NewSpanContext(trace.SpanContextConfig{
		TraceID: request.GetTraceId_High(), //TODO merge request.GetTraceId_High() and request.GetTraceId_Low()
		SpanID: request.GetSpanId(),
	})
	ctx := trace.ContextWithSpanContext(context.Background(), span_ctx)

	tracer := otel.Tracer("ioam-tracer")
	_, span := tracer.Start(ctx, "ioam-span")

	i := 1
	for _, node := range request.GetNodes() {
		str := ParseNode(node, request.GetBitField())
		span.SetAttributes("ioam_namespace" + strconv.FormatUint(uint64(request.GetNamespaceId()), 10) +"_node" + strconv.Itoa(i), str)
		i += 1
	}

	span.End()
	return new(empty.Empty), nil
}

func ParseNode(node *ioam_api.IOAMNode, fields uint32) string {
	str := ""

	if (fields & HAS_HOPLIMIT) != 0 {
		str += "HopLimit=" + strconv.FormatUint(uint64(node.GetHopLimit()), 10) + "; "
	}
	if (fields & HAS_ID) != 0 {
		str += "Id=" + strconv.FormatUint(uint64(node.GetId()), 10) + "; "
	}
	if (fields & HAS_IDWIDE) != 0 {
		str += "IdWide=" + strconv.FormatUint(uint64(node.GetIdWide()), 10) + "; "
	}
	if (fields & HAS_INGRESSID) != 0 {
		str += "IngressId=" + strconv.FormatUint(uint64(node.GetIngressId()), 10) + "; "
	}
	if (fields & HAS_INGRESSIDWIDE) != 0 {
		str += "IngressIdWide=" + strconv.FormatUint(uint64(node.GetIngressIdWide()), 10) + "; "
	}
	if (fields & HAS_EGRESSID) != 0 {
		str += "EgressId=" + strconv.FormatUint(uint64(node.GetEgressId()), 10) + "; "
	}
	if (fields & HAS_EGRESSIDWIDE) != 0 {
		str += "EgressIdWide=" + strconv.FormatUint(uint64(node.GetEgressIdWide()), 10) + "; "
	}
	if (fields & HAS_TIMESTAMPSECS) != 0 {
		str += "TimestampSecs=" + strconv.FormatUint(uint64(node.GetTimestampSecs()), 10) + "; "
	}
	if (fields & HAS_TIMESTAMPFRAC) != 0 {
		str += "TimestampFrac=" + strconv.FormatUint(uint64(node.GetTimestampFrac()), 10) + "; "
	}
	if (fields & HAS_TRANSITDELAY) != 0 {
		str += "TransitDelay=" + strconv.FormatUint(uint64(node.GetTransitDelay()), 10) + "; "
	}
	if (fields & HAS_QUEUEDEPTH) != 0 {
		str += "QueueDepth=" + strconv.FormatUint(uint64(node.GetQueueDepth()), 10) + "; "
	}
	if (fields & HAS_CSUMCOMP) != 0 {
		str += "CsumComp=" + strconv.FormatUint(uint64(node.GetCsumComp()), 10) + "; "
	}
	if (fields & HAS_BUFFEROCCUPANCY) != 0 {
		str += "BufferOccupancy=" + strconv.FormatUint(uint64(node.GetBufferOccupancy()), 10) + "; "
	}
	if (fields & HAS_NAMESPACEDATA) != 0 {
		str += "NamespaceData=0x" + hex.EncodeToString(node.GetNamespaceData()) + "; "
	}
	if (fields & HAS_NAMESPACEDATAWIDE) != 0 {
		str += "NamespaceDataWide=0x" + hex.EncodeToString(node.GetNamespaceDataWide()) + "; "
	}
	if (fields & HAS_OSS) != 0 {
		str += "OpaqueStateSchemaId=" + strconv.FormatUint(uint64(node.GetOSS().GetSchemaId()), 10) + "; "
		str += "OpaqueStateData=0x" + hex.EncodeToString(node.GetOSS().GetData()) + "; "
	}

	return str
}
