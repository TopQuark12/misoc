from liteeth.common import *
from liteeth.generic import *
from liteeth.generic.depacketizer import LiteEthDepacketizer
from liteeth.generic.packetizer import LiteEthPacketizer
from liteeth.generic.crossbar import LiteEthCrossbar

class LiteEthUDPDepacketizer(LiteEthDepacketizer):
	def __init__(self):
		LiteEthDepacketizer.__init__(self,
			eth_ipv4_user_description(8),
			eth_udp_description(8),
			udp_header,
			udp_header_len)

class LiteEthUDPPacketizer(LiteEthPacketizer):
	def __init__(self):
		LiteEthPacketizer.__init__(self,
			eth_udp_description(8),
			eth_ipv4_user_description(8),
			udp_header,
			udp_header_len)

class LiteEthUDPMasterPort:
	def __init__(self, dw):
		self.dw = dw
		self.source = Source(eth_udp_user_description(dw))
		self.sink = Sink(eth_udp_user_description(dw))

class LiteEthUDPSlavePort:
	def __init__(self, dw):
		self.dw =dw
		self.sink = Sink(eth_udp_user_description(dw))
		self.source = Source(eth_udp_user_description(dw))

class LiteEthUDPUserPort(LiteEthUDPSlavePort):
	def __init__(self, dw):
		LiteEthUDPSlavePort.__init__(self, dw)

class LiteEthUDPCrossbar(LiteEthCrossbar):
	def __init__(self):
		LiteEthCrossbar.__init__(self, LiteEthUDPMasterPort, "dst_port")

	def get_port(self, udp_port, dw=8):
		if udp_port in self.users.keys():
			raise ValueError("Port {0:#x} already assigned".format(udp_port))
		user_port = LiteEthUDPUserPort(dw)
		internal_port = LiteEthUDPUserPort(8)
		if dw != 8:
			converter = Converter(eth_udp_user_description(user_port.dw), eth_udp_user_description(8))
			self.submodules += converter
			self.comb += [
				Record.connect(user_port.sink, converter.sink),
				Record.connect(converter.source, internal_port.sink)
			]
			converter = Converter(eth_udp_user_description(8), eth_udp_user_description(user_port.dw))
			self.submodules += converter
			self.comb += [
				Record.connect(internal_port.source, converter.sink),
				Record.connect(converter.source, user_port.source)
			]
			self.users[udp_port] = internal_port
		else:
			self.users[udp_port] = user_port
		return user_port
