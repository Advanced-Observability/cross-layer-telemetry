import sys
import os
import os.path
import getopt
import socket
import grpc
import ioam_trace_pb2
import ioam_trace_pb2_grpc
from bitstruct import unpack

ETH_P_IPV6 = 0x86DD

IPV6_TLV_IOAM = 32
IOAM_PREALLOC_TRACE = 0

TRACE_BIT0  = 1 << 31	# Hop_Lim + Node Id (short)
TRACE_BIT1  = 1 << 30	# Ingress/Egress Ids (short)
TRACE_BIT2  = 1 << 29	# Timestamp seconds
TRACE_BIT3  = 1 << 28	# Timestamp subseconds
TRACE_BIT4  = 1 << 27	# Transit Delay
TRACE_BIT5  = 1 << 26	# Namespace Data (short)
TRACE_BIT6  = 1 << 25	# Queue depth
TRACE_BIT7  = 1 << 24	# Checksum Complement
TRACE_BIT8  = 1 << 23	# Hop_Lim + Node Id (wide)
TRACE_BIT9  = 1 << 22	# Ingress/Egress Ids (wide)
TRACE_BIT10 = 1 << 21	# Namespace Data (wide)
TRACE_BIT11 = 1 << 20	# Buffer Occupancy
TRACE_BIT22 = 1 << 9	# Opaque State Snapshot

BITFIELD_BIT0 = 1 << 31 # Hop_Lim
BITFIELD_BIT1 = 1 << 30 # Node Id
BITFIELD_BIT2 = 1 << 29 # Ingress Id
BITFIELD_BIT3 = 1 << 28 # Egress Id
BITFIELD_BIT4 = 1 << 27 # Timestamp seconds
BITFIELD_BIT5 = 1 << 26 # Timestamp subseconds
BITFIELD_BIT6 = 1 << 25 # Transit Delay
BITFIELD_BIT7 = 1 << 24 # Queue depth
BITFIELD_BIT8 = 1 << 23 # Buffer Occupancy
BITFIELD_BIT9 = 1 << 22 # Namespace Data
BITFIELD_BIT10 = 1 << 21 # Opaque State Snapshot


def help():
	print("Syntax: "+ os.path.basename(__file__) +" -i <interface>")

def help_str(err):
	print(err)
	help()

def interface_exists(interface):
	try:
		socket.if_nametoindex(interface)
		return True

	except OSError:
		return False

def report_ioam(stub, traces):
	try:
		for trace in traces:
			if ((trace.TraceId_High != 0 or trace.TraceId_Low != 0)
			    and trace.SpanId != 0):
				stub.Report(trace)
	except grpc.RpcError as e:
		# IOAM collector is probably not online
		pass

def type2bitfield(trace_type):
	bitfield = 0

	if trace_type & (TRACE_BIT0 | TRACE_BIT8):
		bitfield |= (BITFIELD_BIT0 | BITFIELD_BIT1)
	if trace_type & (TRACE_BIT1 | TRACE_BIT9):
		bitfield |= (BITFIELD_BIT2 | BITFIELD_BIT3)
	if trace_type & TRACE_BIT2:
		bitfield |= BITFIELD_BIT4
	if trace_type & TRACE_BIT3:
		bitfield |= BITFIELD_BIT5
	if trace_type & TRACE_BIT4:
		bitfield |= BITFIELD_BIT6
	if trace_type & (TRACE_BIT5 | TRACE_BIT10):
		bitfield |= BITFIELD_BIT9
	if trace_type & TRACE_BIT6:
		bitfield |= BITFIELD_BIT7
	if trace_type & TRACE_BIT11:
		bitfield |= BITFIELD_BIT8
	if trace_type & TRACE_BIT22:
		bitfield |= BITFIELD_BIT10

	return bitfield

def parse_node_data(data, trace_type):
	node = ioam_trace_pb2.IOAMNode()

	i = 0
	if trace_type & TRACE_BIT0:
		node.HopLimit, node.Id = unpack(">u8u24", data[i:i+4])
		i += 4
	if trace_type & TRACE_BIT1:
		node.IngressId, node.EgressId = unpack(">u16u16", data[i:i+4])
		i += 4
	if trace_type & TRACE_BIT2:
		node.Timestamp = unpack(">u32", data[i:i+4])[0]
		i += 4
	if trace_type & TRACE_BIT3:
		node.TimestampSub = unpack(">u32", data[i:i+4])[0]
		i += 4
	if trace_type & TRACE_BIT4:
		node.TransitDelay = unpack(">u32", data[i:i+4])[0]
		i += 4
	if trace_type & TRACE_BIT5:
		node.Data = unpack(">r32", data[i:i+4])[0]
		i += 4
	if trace_type & TRACE_BIT6:
		node.EgressQDepth = unpack(">u32", data[i:i+4])[0]
		i += 4
	if trace_type & TRACE_BIT7:
		i += 4
	if trace_type & TRACE_BIT8:
		node.HopLimit, node.WideId = unpack(">u8u56", data[i:i+8])
		i += 8
	if trace_type & TRACE_BIT9:
		node.IngressId, node.EgressId = unpack(">u32u32", data[i:i+8])
		i += 8
	if trace_type & TRACE_BIT10:
		node.WideData = unpack(">r32", data[i:i+8])[0]
		i += 8
	if trace_type & TRACE_BIT11:
		node.BufferOccupancy = unpack(">u32", data[i:i+4])[0]
		i += 4

	return node

def parse_ioam_trace(data):
	try:
		nsId, node_len, _, remaining_len, trace_type, \
		  trace_id, span_id = unpack(">u16u5u4u7u32u128u64", data[:32])

		nodes = []
		i = 32 + remaining_len * 4

		while i < len(data):
			node = parse_node_data(data[i:i+node_len*4], trace_type)
			i += node_len * 4

			if trace_type & TRACE_BIT22:
				opaque_len, node.OSS.SchemaId = unpack(">u8u24",
								data[i:i+4])
				if opaque_len > 0:
					node.OSS.Data = data[i+4:i+4+opaque_len]

				i += 4 + opaque_len * 4

			nodes.insert(0, node)

		trace = ioam_trace_pb2.IOAMTrace()
		trace.BitField = type2bitfield(trace_type)
		trace.NamespaceId = nsId
		trace.TraceId_High = trace_id >> 64
		trace.TraceId_Low = trace_id & 0x0000000000000000ffffffffffffffff
		trace.SpanId = span_id
		trace.Nodes.extend(nodes)

		return trace
	except:
		return None

def parse(packet):
	try:
		nextHdr = packet[6]
		if nextHdr != socket.IPPROTO_HOPOPTS:
			return None

		hbh_len = (packet[41] + 1) << 3
		i = 42

		traces = []
		while hbh_len > 0:
			opt_type, opt_len, _, ioam_type = unpack(">u8u8u8u8",
								 packet[i:i+4])
			opt_len += 2

			if (opt_type == IPV6_TLV_IOAM and
			    ioam_type == IOAM_PREALLOC_TRACE):

				trace = parse_ioam_trace(packet[i+4:i+opt_len])
				if trace is not None:
					traces.append(trace)

			i += opt_len
			hbh_len -= opt_len

		return traces
	except:
		return None

def listen(interface, collector):
	try:
		sock = socket.socket(socket.AF_PACKET,
				     socket.SOCK_DGRAM,
				     socket.htons(ETH_P_IPV6))

		sock.setsockopt(socket.SOL_SOCKET,
				socket.SO_BINDTODEVICE,
				interface.encode())

		channel = grpc.insecure_channel(collector)
		stub = ioam_trace_pb2_grpc.IOAMServiceStub(channel)

		print("[IOAM Agent] Reporting to IOAM collector...")
		while True:
			traces = parse(sock.recv(65565))

			if traces is not None:
				report_ioam(stub, traces)

	except KeyboardInterrupt:
		print("[IOAM Agent] Closing...")
	except Exception as e:
		print("[IOAM Agent] Closing on unexpected error: "+ str(e))
	finally:
		channel.close()
		sock.close()

def main(script, argv):
	try:
		opts, args = getopt.getopt(argv, "hi:", ["interface="])

	except getopt.GetoptError:
		help()
		sys.exit(1)

	interface = ""
	for opt, arg in opts:
		if opt == '-h':
			help()
			sys.exit()

		if opt in ("-i", "--interface"):
			interface = arg

	if not interface_exists(interface):
		help_str("Unknown interface "+ interface)
		sys.exit(1)

	try:
		collector = os.environ['IOAM_COLLECTOR']
		listen(interface, collector)
	except KeyError:
		print("IOAM collector is not defined")
		sys.exit(1)

if __name__ == "__main__":
	main(sys.argv[0], sys.argv[1:])
