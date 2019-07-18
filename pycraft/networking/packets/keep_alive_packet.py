from minecraft.networking.types import (
    VarInt, Long
)

from .packet import Packet


class AbstractKeepAlivePacket(Packet):
    packet_name = "keep alive"
    get_definition = staticmethod(lambda context: [
        {'keep_alive_id': Long} if context.protocol_version >= 339
        else {'keep_alive_id': VarInt}
    ])


# This alias is retained for backward compatibility:
KeepAlivePacket = AbstractKeepAlivePacket
