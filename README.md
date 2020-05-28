# Cross Layer Telemetry

This project, based on IPv6 IOAM in the kernel, aims to make the entire stack (L2/L3 -> L7) visible for distributed tracing tools, thanks to a correlation in [Jaeger](https://www.jaegertracing.io) between trace/span IDs carried in the dataplane by IOAM and [OpenTelemetry](https://opentelemetry.io) data.

Both the Trace ID (either 64 or 128 bits) and the Span ID are carried by IOAM, right after the IOAM Trace Option Header, to avoid a collision at correlation time.

![IOAM_Trace_Header_Span](./images/ioam_new_header.png?raw=true "Location of Trace and Span IDs in the IOAM Trace Option header")

### Installation

First, you need a kernel with IOAM. If you don't have one, please follow [this section](https://github.com/IurmanJ/kernel_ipv6_ioam#patching-the-kernel).

For Cross Layer Telemetry, you also need to patch the IOAM kernel with this [new CLT patch](CLT.patch) before compiling.

### Tools

Docker and Docker-compose are used to build the topology. Recommended versions:
```
$ docker --version
Docker version 19.03.6, build 369ce74a3c

$ docker-compose --version
docker-compose version 1.25.5, build 8a1c60f6
```

Docker images have been built for a Linux/amd64 (x86_64) platform. If that does not match your need, you can [regenerate them](./demo/images/) by running:
```
./build_images.sh
```

### Topology

An HTTP client request to an API entrypoint is simulated, which one triggers two sub-requests to a server. Inside the IOAM domain, the tracing (agents & collector) is achieved with Jaeger while IOAM has its own agent and collector to correlate dataplane data with Trace/Span IDs from Jaeger. A querier is available to visualize tracing results with IOAM data.

![Topology](images/topology.png?raw=true "Topology")

### Demo

If you want to test it, make sure you have an IOAM kernel patched for CLT, go to the demo folder and run:
```
./topology_setup.sh
```

Click on the GIF below to watch the demo video:
[![GIF_video](./images/video.gif?raw=true "CLT demo video")](https://youtu.be/dpyChGrEwVs)
