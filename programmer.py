from struct import pack
from crc16 import crc16xmodem
from ec3 import EC3Error

ProgramError = EC3Error

class PageData(object):
	def __init__(self, addr, page, data):
		self.addr = addr
		self.page = page
		self.data = data
		self.crc = crc16xmodem(data)

	def ProgramVerify(self, da):
		da.SetCodeMem(self.addr, self.data)
		if da.GetPageCRC(self.page)!=self.crc:
			raise ProgramError("Page %X CRC mismatch" % (self.page))			

#################################################################################

class DeviceProgrammer(object):
	def __init__(self, data="", addr=0, page_size=0x100, sn_addr=-1):
		if addr % page_size:
			raise ProgramError("Programming start address is not on a page boundary")

		size = len(data)
		if size % page_size:
			raise ProgramError("Programming data size is not a multiple of page size")

		if sn_addr!=-1:
			if (sn_addr % page_size)>(page_size-4):
				raise ProgramError("Serial number area crosses page boundary")
			self.sn_page = sn_addr//page_size
			self.sn_offset = sn_addr % page_size
			self.sn_base = sn_addr-self.sn_offset
		else:
			self.sn_page = -1

		self.page_size = page_size
		self.empty_page = b"\xFF"*page_size

		self.fixed_pages = []		
		for ofs in range(0, size, page_size):
			page = (addr+ofs)//page_size
			pg_data = data[ofs:ofs+page_size]
			if page==self.sn_page:
				self.pre_sn_data = pg_data[0:self.sn_offset]
				self.post_sn_data = pg_data[self.sn_offset+4:]
			else: # fixed page
				self.fixed_pages.append(PageData(addr+ofs, page, pg_data))


	def ProgramDevice(self, da, board_sn=-1):
		if board_sn!=-1 and self.sn_page==-1:
			raise ProgramError("Programmer was not initialized for s/n handling")
		if board_sn!=-1:
			data = self.pre_sn_data+pack("<L", board_sn)+self.post_sn_data
			da.SetCodeMem(self.sn_base, data)
			if da.GetPageCRC(self.sn_page)!=crc16xmodem(data):
				raise ProgramError("S/N page %X CRC mismatch" % (self.sn_page))			
		for page in self.fixed_pages:
			page.ProgramVerify(da)


__all__ = ["DeviceProgrammer"]
