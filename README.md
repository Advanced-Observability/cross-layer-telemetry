# ~~Cross Layer Telemetry~~ ARCHIVED

**Note: this version is deprecated and is still available for information.**

The *Cross-Layer Telemetry* (CLT) project, based on [IOAM](https://tools.ietf.org/html/draft-ietf-ippm-ioam-data) ([for IPv6](https://tools.ietf.org/html/draft-ietf-ippm-ioam-ipv6-options)) in the Linux kernel, aims to make the entire network stack (L2 -> L7) visible for distributed tracing tools instead of the classic L5 -> L7 visibility.

The chosen Application Performance Management (APM) tool, based on distributed tracing, is [Jaeger](https://www.jaegertracing.io), although CLT is generic enough to work with other alternatives. A correlation between APM traces (trace and span IDs from Jaeger) and network telemetry (IOAM data in packets) is now possible. Indeed, both trace ID (either 64 or 128 bits) and span ID (64 bits) are carried by IOAM in the dataplane, right after the IOAM Trace Option Header.

![IOAM_Trace_Header_Span](./images/ioam_new_header.png?raw=true "Location of trace and span IDs in the IOAM Trace Option Header")

Some key components are crucial for CLT:

- a recent kernel with IOAM (+ patched for Cross-Layer Telemetry)
- a CLT client library
- an IOAM Agent
- an IOAM Collector

![CLT_Architecture](./images/architecture.png?raw=true "CLT Architecture, with Jaeger as the tracing tool")

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

A client (you) sends a login request to an API entrypoint, which one triggers a sub-request to a server. Inside the (IPv6) IOAM domain, the tracing (agents & collector) is achieved with Jaeger while IOAM has its own agent and collector to correlate dataplane data with Trace/Span IDs from Jaeger.

![Topology](images/topology.png?raw=true "Topology")

### Try it yourself !

If you want to test it, make sure you have an IOAM kernel patched for CLT, then go to the demo folder and run:
```
./topology_setup.sh
```

Once started, and still on the demo folder, open the file `app_login.html` with your browser. You can enter whatever username/password, only clt (username) and clt (password) will succeed. Each login request is recorded and enhanced with IOAM. Follow instructions on the screen and have fun looking at application traces combined with IOAM data.

To simulate a congestion on the router inside the (IPv6) IOAM domain, enter the following command:
```
docker exec porthos /sbin/tc qdisc add dev eth1 root netem delay 1000ms
```

Try again to log you in. You'll notice that the congestion is reported by IOAM inside application traces.

### Video

You can watch the entire demo by clicking on the following video:

[![GIF_video](./images/video.gif?raw=true "CLT demo video")](https://youtu.be/LD1Dv9MPoJ8)
