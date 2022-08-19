from pyroute2.netlink import genlmsg
from pyroute2.netlink import NLM_F_REQUEST, NLM_F_ACK
from pyroute2.netlink.generic import GenericNetlinkSocket

IOAM6_GENL_NAME = 'IOAM6'
IOAM6_GENL_VERSION = 1

IOAM6_CMD_PKT_ID_ENABLE = 8
IOAM6_CMD_PKT_ID_DISABLE = 9

class cltcmd(genlmsg):
    '''
    Message class that will be used to communicate
    with the kernel module.
    '''
    nla_map = (
        ('IOAM6_ATTR_UNSPEC', 'none'),
        ('IOAM6_ATTR_NS_ID', 'uint16'),
        ('IOAM6_ATTR_NS_DATA', 'uint32'),
        ('IOAM6_ATTR_NS_DATA_WIDE', 'uint64'),
        ('IOAM6_ATTR_SC_ID', 'uint32'),
        ('IOAM6_ATTR_SC_DATA', 'cdata'),
        ('IOAM6_ATTR_SC_NONE', 'flag'),
        ('IOAM6_ATTR_PAD', 'none'),
        ('IOAM6_ATTR_SOCKFD', 'uint32'),
        ('IOAM6_ATTR_ID_HIGH', 'uint64'),
        ('IOAM6_ATTR_ID_LOW', 'uint64'),
        ('IOAM6_ATTR_SUBID', 'uint64'),
    )

class CrossLayerTelemetry(GenericNetlinkSocket):
    '''
    Cross-Layer Telemetry (CLT) generic netlink protocol, based on IOAM.
    '''

    def __init__(self):
        GenericNetlinkSocket.__init__(self)
        self.bind(IOAM6_GENL_NAME, cltcmd)

    def enable(self, sockfd, traceId, spanId):
        msg = cltcmd()

        traceId_h = traceId >> 64
        traceId_l = traceId & 0x0000000000000000ffffffffffffffff

        msg['cmd'] = IOAM6_CMD_PKT_ID_ENABLE
        msg['version'] = IOAM6_GENL_VERSION
        msg['attrs'].append(('IOAM6_ATTR_SOCKFD', sockfd))
        msg['attrs'].append(('IOAM6_ATTR_ID_HIGH', traceId_h))
        msg['attrs'].append(('IOAM6_ATTR_ID_LOW', traceId_l))
        msg['attrs'].append(('IOAM6_ATTR_SUBID', spanId))

        return self.nlm_request(msg, msg_type=self.prid, msg_flags=NLM_F_REQUEST | NLM_F_ACK)

    def disable(self, sockfd):
        msg = cltcmd()

        msg['cmd'] = IOAM6_CMD_PKT_ID_DISABLE
        msg['version'] = IOAM6_GENL_VERSION
        msg['attrs'].append(('IOAM6_ATTR_SOCKFD', sockfd))

        return self.nlm_request(msg, msg_type=self.prid, msg_flags=NLM_F_REQUEST | NLM_F_ACK)

