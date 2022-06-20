package main

import (
	"context"
	"encoding/hex"
	"log"
	"net"
	"strconv"
	"time"

	"ioam" //TODO "ioam_trace" instead?
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
	service     = "trace-demo"
	environment = "production"
	id          = 1
)

var HAS_HOP_LIM   = uint32(1 << 31)
var HAS_NODE_ID   = uint32(1 << 30)
var HAS_INGRESS   = uint32(1 << 29)
var HAS_EGRESS    = uint32(1 << 28)
var HAS_TIMESTAMP = uint32(1 << 27)
var HAS_TIMESTSUB = uint32(1 << 26)
var HAS_TRANSITD  = uint32(1 << 25)
var HAS_EGRESS_QD = uint32(1 << 24)
var HAS_BUFFER_OC = uint32(1 << 23)
var HAS_NS_DATA   = uint32(1 << 22)
var HAS_OPAQUE    = uint32(1 << 21)

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
	ioam_trace.RegisterIOAMServiceServer(grpcServer, server)
	listen, err := net.Listen("tcp", ":7123")
	if err != nil {
		log.Fatalf("could not listen: %v", err)
	}

	log.Println("IOAM collector starting...")
	log.Fatal(grpcServer.Serve(listen))
}

type Server struct{}

func (Server) Report(grpc_ctx context.Context, request *ioam_trace.IOAMTrace) (*empty.Empty, error) {
	span_ctx := trace.NewSpanContext(trace.SpanContextConfig{
		TraceID: xxx, //TODO merge request.GetTraceId_High() and request.GetTraceId_Low()
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

func ParseNode(node *ioam_trace.IOAMNode, fields uint32) string {
	str := ""

	if (fields & HAS_HOP_LIM) != 0 {
		str += "Hop_Limit=" + strconv.FormatUint(uint64(node.GetHopLimit()), 10) + "; "
	}
	if (fields & HAS_NODE_ID) != 0 {
		switch node.GetNode().(type) {
		case *ioam_trace.IOAMNode_Id:
			str += "Node_Id=" + strconv.FormatUint(uint64(node.GetId()), 10) + "; "
		case *ioam_trace.IOAMNode_WideId:
			str += "Node_WideId=" + strconv.FormatUint(uint64(node.GetWideId()), 10) + "; "
		}
	}
	if (fields & HAS_INGRESS) != 0 {
		str += "Ingress_Id=" + strconv.FormatUint(uint64(node.GetIngressId()), 10) + "; "
	}
	if (fields & HAS_EGRESS) != 0 {
		str += "Egress_Id=" + strconv.FormatUint(uint64(node.GetEgressId()), 10) + "; "
	}
	if (fields & HAS_TIMESTAMP) != 0 {
		str += "Timestamp=" + strconv.FormatUint(uint64(node.GetTimestamp()), 10) + "; "
	}
	if (fields & HAS_TIMESTSUB) != 0 {
		str += "Timestamp_Sub=" + strconv.FormatUint(uint64(node.GetTimestampSub()), 10) + "; "
	}
	if (fields & HAS_TRANSITD) != 0 {
		str += "Transit_Delay=" + strconv.FormatUint(uint64(node.GetTransitDelay()), 10) + "; "
	}
	if (fields & HAS_EGRESS_QD) != 0 {
		str += "Egress_Queue_Depth=" + strconv.FormatUint(uint64(node.GetEgressQDepth()), 10) + "; "
	}
	if (fields & HAS_BUFFER_OC) != 0 {
		str += "Buffer_Occupancy=" + strconv.FormatUint(uint64(node.GetBufferOccupancy()), 10) + "; "
	}
	if (fields & HAS_NS_DATA) != 0 {
		switch node.GetNamespace().(type) {
		case *ioam_trace.IOAMNode_Data:
			str += "Namespace_Data=0x" + hex.EncodeToString(node.GetData()) + "; "
		case *ioam_trace.IOAMNode_WideData:
			str += "Namespace_WideData=0x" + hex.EncodeToString(node.GetWideData()) + "; "
		}
	}
	if (fields & HAS_OPAQUE) != 0 {
		str += "Opaque_State_Schema_Id=" + strconv.FormatUint(uint64(node.GetOSS().GetSchemaId()), 10) + "; "
		str += "Opaque_State_Data=0x" + hex.EncodeToString(node.GetOSS().GetData()) + "; "
	}

	return str
}
