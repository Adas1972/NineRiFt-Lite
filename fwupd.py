from py9b.link.base import LinkOpenException, LinkTimeoutException
from py9b.transport.base import BaseTransport as BT
from py9b.transport.xiaomi import XiaomiTransport
from py9b.transport.ninebot import NinebotTransport
from py9b.command.regio import ReadRegs, WriteRegs
from py9b.command.update import *

class FWUpd():
	def __init__(self):
		self.PING_RETRIES = 20
		self.devices = {'ble': BT.BLE, 'esc': BT.ESC, 'bms': BT.BMS, 'extbms': BT.EXTBMS}
		self.protocols = {'xiaomi': XiaomiTransport, 'ninebot': NinebotTransport}
		self.device = ''
		self.fwfilep = ''
		self.interface = 'bleandroid'
		self.protocol = 'ninebot'
		self.address = ''

	def setaddr(a):
		global self.address
		self.address = a
		print(self.address+' selected as address')

	def setdev(d):
		global self.device
		self.device = d
		print(self.device+' selected as device')

	def setfwfilep(f):
		global self.fwfilep
		self.fwfilep = f
		print(self.fwfilep+' selected as fwfile')

	def setinterface(i):
		global self.interface
		self.interface = i
		print(self.interface+' selected as interface')

	def setproto(p):
		global self.protocol
		self.protocol = p
		print(self.protocol+' selected as protocol')

	def checksum(s, data):
		for c in data:
			s += ord(c)
		return (s & 0xFFFFFFFF)

	def UpdateFirmware(link, tran, dev, fwfile):
		print('flashing '+self.fwfilep+' to '+ self.device)
		fwfile.seek(0, os.SEEK_END)
		fw_size = fwfile.tell()
		fwfile.seek(0)
		fw_page_size = 0x80

		dev = self.devices.get(self.device)
		print('Pinging...')
		for retry in range(self.PING_RETRIES):
			print('.')
			try:
				if dev==BT.BLE:
					tran.execute(ReadRegs(dev, 0, '13s'))
				else:
					tran.execute(ReadRegs(dev, 0x10, '14s'))
			except LinkTimeoutException:
				continue
			break
		else:
			print('Timed out !')
			return False
		print('OK')

		if self.interface!='tcpnl':
			print('Locking...')
			tran.execute(WriteRegs(BT.ESC, 0x70, '<H', 0x0001))
		else:
			print('Not Locking...')

		print('Starting...')
		tran.execute(StartUpdate(dev, fw_size))

		print('Writing...')
		page = 0
		chk = 0
		while fw_size:
			chunk_sz = min(fw_size, fw_page_size)
			data = fwfile.read(chunk_sz)
			chk = checksum(chk, data)
			#tran.execute(WriteUpdate(dev, page, data))
			tran.execute(WriteUpdate(dev, page, data+b'\x00'*(fw_page_size-chunk_sz))) # TODO: Ninebot wants this padding. Will it work on M365 too?
			page += 1
			fw_size -= chunk_sz

		print('Finalizing...')
		tran.execute(FinishUpdate(dev, chk ^ 0xFFFFFFFF))

		print('Reboot')
		tran.execute(RebootUpdate(dev))
		print('Done')
		return True

	def Flash(self, self.fwfilepath):
		if self.device=='extbms' and self.protocol!='ninebot':
			exit('Only Ninebot supports External BMS !')
		setself.fwfilep(self.fwfilepath)
		file = open(self.fwfilep, 'rb')
		dev = self.devices.get(self.device)
		if self.interface=='bleandroid':
			try:
				from py9b.link.bleandroid import BLELink
			except:
				exit('BLE is not supported on your system !')
			link = BLELink()
		elif self.interface=='tcp':
			from py9b.link.tcp import TCPLink
			link = TCPLink()
		elif self.interface=='serial':
			from py9b.link.serial import SerialLink
			link = SerialLink()
		else:
			exit('!!! BUG !!! Unknown self.interface selected: '+self.interface)

		with link:
			tran = self.protocols.get(self.protocol)(link)

			if self.address!='':
				addr = self.address
			elif self.interface!='bleandroid':
				print('Scanning...')
				ports = link.scan()
				if not ports:
					exit("No self.interfaces found !")
				print('Connecting to', ports[0][0])
				addr = ports[0][1]
			else:
				raise LinkOpenException

			link.open(addr)
			print('Connected')
			try:
				UpdateFirmware(link, tran, dev, file)
			except Exception as e:
				print('Error:', e)
				raise
