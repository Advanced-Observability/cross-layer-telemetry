# CLT Library

This library allows to enable or disable CLT in the Linux kernel by using [generic netlink](https://docs.kernel.org/networking/generic_netlink.html) to interact with the kernel.

## Usage

The implementations **must** provide 2 methods:
- One to **enable** CLT on a given socket with given trace and span IDs.
- One to **disable** CLT on a given socket.

## Existing implementations

At the moment, implementations are available in the following languages:
- [Python](./python/)
- [Go](./golang/)
