# CLT Generic Netlink Go

This module allows to enable or disable CLT in the Linux kernel from software in Go.

It is an equivalent of [clt_genl.py](../clt_genl.py), which is written in Python.

## Usage

First, you need to download the dependencies with the following command:
```bash
go mod download
```

Then, you can enable CLT on a socket using the method:
```go
func clt_enable(socketFD uint32, traceIDHigh uint64, traceIDLow uint64, spanID uint64) error
```

Finally, when you want to disable CLT, you can use the method:
```go
func clt_disable(socketFD uint32) error
```

## Credits

To use (generic) netlink in Go, we use the packages [netlink](https://github.com/mdlayher/netlink) and [genetlink](https://github.com/mdlayher/genetlink) by [Matt Layher](https://github.com/mdlayher).
