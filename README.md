# Cross Layer Telemetry

The *Cross-Layer Telemetry* (CLT) project is based on [IOAM](https://datatracker.ietf.org/doc/rfc9197/) ([for IPv6](https://datatracker.ietf.org/doc/draft-ietf-ippm-ioam-ipv6-options)) in the Linux kernel and aims to make the entire network stack (L2 -> L7) visible for distributed tracing tools instead of the classic L5 -> L7 visibility.

The chosen Application Performance Management (APM) tool based on distributed tracing is [OpenTelemetry](https://opentelemetry.io), which is the new standard. The chosen backend for data visualization is [Jaeger](https://www.jaegertracing.io), although CLT is generic enough to work with other backends. Only the IOAM collector, an interface between the IOAM agent and a tracing backend, is backend-specific and can easily be implemented for other alternatives than Jaeger.

## How does it work?

![CLT_Architecture](./images/architecture.png?raw=true "CLT Architecture, with OpenTelemetry as the tracing tool and Jaeger as the backend")

Some key components are crucial for the CLT ecosystem:
- a recent kernel with IOAM (>= 5.17) [patched](./CLT.patch) for Cross-Layer Telemetry
- the CLT client library in [Python](./library/python/clt_genl.py) or in [Go](./library/golang/clt_genl.go)
- an [IOAM Agent](https://github.com/Advanced-Observability/ioam-agent-python/tree/clt)
- an [IOAM Collector](https://github.com/Advanced-Observability/ioam-collector-go-jaeger)

CLT correlates APM traces with network telemetry, based on APM trace and span IDs. Both IDs are carried by IOAM in the dataplane, right after the IOAM Pre-allocated Trace Option-Type Header. As a result, APM traces in data visualization will include network telemetry.

![IOAM_Trace_Header_Span](./images/ioam_new_header.png?raw=true "Location of trace and span IDs in the IOAM Pre-allocated Trace Option-Type Header")

## Video demo

You can watch the entire demo by clicking on the following video:

[![video]()](https://github.com/user-attachments/assets/c780416d-8b0c-48fe-9c1a-865ab4de2e28)

Note: this video was for a previous version of CLT, but it's still the same result globally.

## Example

A client (mobile phone) sends a login request to an API entrypoint, which one triggers a sub-request to a server. The monitoring happens inside the (IPv6) IOAM domain, i.e., each request between the API entrypoint and the server.

![Topology](images/topology.png?raw=true "Topology")

## Try it !

Prerequisites:
- an IOAM kernel (>= 5.17) patched for CLT
- docker installed (tested with: `Docker version 20.10.17, build 100c701`)
- docker-compose installed (tested with: `docker-compose version 1.25.5, build 8a1c60f6`)

Go to the [demo](./demo) folder and run the following command to build the virtual topology (the same as the example above):
```
docker-compose up -d
```

Once started, open [app_login.html](./demo/app_login.html) in your browser. You can enter whatever username/password you want, but only `clt` (username) and `clt` (password) will succeed. Each login request is recorded and enhanced with network telemetry (thanks to IOAM data). Follow instructions on the screen and have fun looking at enhanced application traces.

To simulate a congestion on the router inside the (IPv6) IOAM domain, enter the following command:
```
docker exec porthos /sbin/tc qdisc add dev eth1 root netem delay 1000ms
```

Try again to log you in. You'll notice that the congestion is reported by IOAM inside application traces. You might need several simultaneous login attempts to see it, so that the queue starts filling.

When you're done, just run:
```
docker-compose down
```
