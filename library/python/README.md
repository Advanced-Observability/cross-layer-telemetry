# CLT Library in Python

Implementation in Python of the library to enable or disable CLT.

## Usage

First, you need to download the dependency with the following command:
```bash
pip3 install pyroute2
```

Then, you need to create an instance of the class `CrossLayerTelemetry`.

Now, you can enable CLT on a socket by calling the method:
```python
def enable(self, sockfd, traceId, spanId)
```

Finally, when you want to disable CLT, you can call the method:
```python
def disable(self, sockfd)
```

## Credits

To use (generic) netlink in Python, we use the package [pyroute2](https://pypi.org/project/pyroute2/) by [Peter Saveliev](https://github.com/svinota).
