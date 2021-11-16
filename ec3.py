#!/usr/bin/python3

__all__ = ['EC3Error', 'EC3']

from struct import pack, unpack
from ctypes import c_ubyte
import hid

# total max report size is 64 bytes (1 byte id + 63 bytes payload)
MAX_REPORT_SIZE = 64

FW_VERSION = 0x26

# 64-(report_id[1]+cmd[1]+addr[1]+data_len[1])
WBLK8_CHUNK_SIZE = 60

# 64-(report_id[1]+cmd[1]+addr[2]+data_len[1])
WBLK16_CHUNK_SIZE = 59

# 64-(report_id[1]+status[1])
RBLK_CHUNK_SIZE = 62

ErrorCodes = {  0x0D : "OK",
				0x01 : "Target is not in the HALT state and did not respond to the query.",
				0x02 : "The target reported that the command failed.",
				0x03 : "A Flash failure has occurred, most likely due to locked flash.",
				0x57 : "The target is not responding." }

class EC3Error(Exception):
	pass

class EC3(object):
	def __init__(self, sn=None, dump=False):
		self.dump = dump
		self.sn = sn

		self.connected = False		
		self.last_error = ""
		self.dev = None
		self.rx_timeout = 1500
		buf_type = c_ubyte * 65
		self.last_report = buf_type()
		
		self.HardwareID = 0
		self.HardwareRev = 0
		self.DebugLogicVersion = 0
		self.DerivativeID = 0


	def open(self):
		if self.dev:
			self.dev.close()
			self.dev = None
		try:
			self.dev = hid.Device(vid=0x10C4, pid=0x8044, serial=self.sn)
		except:
			raise
			#raise EC3Error("No EC3 adapters found")
			

	def close(self):
		if self.dev:
			self.dev.close()
			self.dev = None
	
	################## HID level io ################################

	def control(self, data):
		if self.dump:
			print("CTRL>", data.hex())
		self.dev.send_feature_report(data)


	def tx(self, data):
		#self.dev.send_output_report(chr(len(data))+data)
		if self.dump:
			print(">", data.hex())
		self.dev.write(pack('<B', len(data))+data)


	def rx(self):
		res = self.dev.read(MAX_REPORT_SIZE, timeout=self.rx_timeout)
		ll = res[0]
		rsp = res[1:ll+1]
		if self.dump:
			print("<", rsp.hex())
		return rsp

	###############################################################

	def txrx(self, outdata, insize, err_msg=""):
		self.tx(outdata)
		rsp = self.rx()
		if len(rsp)!=insize:
			raise EC3Error(err_msg+": Invalid response len")
		return rsp
		

	def cmd(self, cmd, outdata=b"", insize=0, err_msg=""):
		self.tx(pack('<B', cmd)+outdata)
		rsp = self.rx()
		res = rsp[-1]
		if res!=0x0D:
			raise EC3Error(err_msg+": "+ErrorCodes.get(res, "Unknown error"))
		if len(rsp)!=insize+1:
			raise EC3Error(err_msg+": Invalid response len")
		return rsp[0:-1]


	def wblk8(self, cmd, addr, data=b"", err_msg=""):
		size = len(data)
		ofs = 0
		while size:
			chunk_size = min(size, WBLK8_CHUNK_SIZE)
			self.cmd(cmd, pack("BB", addr+ofs, chunk_size)+data[ofs:ofs+chunk_size], err_msg=err_msg)
			ofs += chunk_size
			size -= chunk_size
		

	def wblk16(self, cmd, addr, data=b"", err_msg=""):
		size = len(data)
		ofs = 0
		while size:
			chunk_size = min(size, WBLK16_CHUNK_SIZE)
			self.cmd(cmd, pack("<HB", addr+ofs, chunk_size)+data[ofs:ofs+chunk_size], err_msg=err_msg)
			ofs += chunk_size
			size -= chunk_size
		

	def rblk8(self, cmd, addr, size, err_msg=""):
		data = b""
		ofs = 0
		while size:
			chunk_size = min(size, RBLK_CHUNK_SIZE)
			data += self.cmd(cmd, pack("<BB", addr+ofs, chunk_size), chunk_size, err_msg=err_msg)
			ofs += chunk_size
			size -= chunk_size
		return data
		

	def rblk16(self, cmd, addr, size, err_msg=""):
		data = b""
		ofs = 0
		while size:
			chunk_size = min(size, RBLK_CHUNK_SIZE)
			data += self.cmd(cmd, pack("<HB", addr+ofs, chunk_size), chunk_size, err_msg=err_msg)
			ofs += chunk_size
			size -= chunk_size
		return data
		
	################# EC3 commands #################################

	##### BL control commands (both modes)

	def ResetAdapter(self):
		self.control(b"\x40\x02\x00\x00")
		rsp = self.rx()
		if len(rsp)!=1:
			raise EC3Error("ResetAdapter: Invalid response len")
		if rsp[0]!=0xFF:
			raise EC3Error("ResetAdapter: error")

	#### BL mode commands 

	def BLGetVersion(self):
		rsp = self.txrx(b"\x00\x00\x00", 1, "BLGetVersion")
		return rsp[0]

	def BLGetOSXFlag(self):
		rsp = self.txrx(b"\x80\x00\x00", 1, "BLGetOSXFlag")
		return rsp[0]

	def BLSetPage(self, pg):
		rsp = self.txrx(pack(">BBB", 1, pg, 0), 1, "BLSetPage")
		if rsp!=b"\x00":
			raise EC3Error("BLSetPage: Error")

	def BLGo(self):
		rsp = self.txrx(b"\x06\x00\x00", 1, "BLGo")
		if rsp[0]!=FW_VERSION:
			print("Warining: different adapter fw version: %02X !" % (rsp[0]))
			# ignoring for now

	def BLReadByte(self, addr):
		rsp = self.txrx(pack(">BH", 5, addr), 1, "BLReadByte")
		return rsp[0]

	#TODO BLErasePAge
	#TODO BLCRCPage
	#TODO BLReadVerify
	#TODO BLProgramPage
	#TODO BLWritePage
	
	#### FW mode commands

	def Connect(self):
		self.cmd(0x20, err_msg="Connect")

	def Disconnect(self):
		self.cmd(0x21, err_msg="Disonnect")

	def IdentifyTarget(self):
		hwid = self.cmd(0x22, insize=2, err_msg="GetHwid")
		if hwid!=b"\xFF\xFF" and hwid!=b"\x00\x00":
			drid = self.cmd(0x23, insize=2, err_msg="GetDerid")
			result = True
		else:
			hwid = b"\xFF\xFF"
			drid = b"\xFF\xFF"
			result = False
		self.HardwareID = hwid[0]
		self.HardwareRev = hwid[1]
		self.DebugLogicVersion = drid[0]
		self.DerivativeID = drid[1]
		return result
		
	def Go(self):
		self.cmd(0x24, err_msg="Go")

	def Halt(self):
		self.cmd(0x25, err_msg="Halt")

	def Step(self):
		self.cmd(0x26, err_msg="Step")

	def GetSFRByte(self, addr):
		return self.cmd(0x28, pack("BB", addr, 1), 1, "GetSFRByte")[0]

	def GetSFRMem(self, addr, size):
		return self.rblk8(0x28, addr, size, "GetSFRMem")

	def SetSFRByte(self, addr, value):
		self.cmd(0x29, pack("BBB", addr, 1, value), err_msg="SetSFRByte")

	def SetSFRMem(self, addr, data):
		self.wblk8(0x29, addr, data, "SetSFRMem")

	def GetDataByte(self, addr):
		return self.cmd(0x2A, pack("<HB", addr, 1), 1, "GetDataByte")[0]
		
	def GetDataMem(self, addr, size):
		return self.rblk16(0x2A, addr, size, "GetDataMem") # TODO: why addr16 here? Is it idata or xdata?
		
	def GetCodeByte(self, addr):
		return self.cmd(0x2E, pack("<HB", addr, 1), 1, "GetCodeByte")[0]
			
	def GetCodeMem(self, addr, size):
		return self.rblk16(0x2E, addr, size, "GetCodeMem")

	def SetCodeByte(self, addr, value):
		self.cmd(0x2F, pack("<HBB", addr, 1, value), err_msg="SetCodeByte")
			
	def SetCodeMem(self, addr, data):
		self.wblk16(0x2F, addr, data, "SetCodeMem")
			
	def ErasePage(self, page):
		self.cmd(0x30, pack('<B', page), err_msg="ErasePage")	

	def GetPageCRC(self, page):
		return unpack(">H", self.cmd(0x31, pack('<B', page), 2, err_msg="GetPageCRC"))[0]

	def IndGetSFRByte(self, addr):
		return self.cmd(0x36, pack("BB", addr, 1), 1, "IndGetSFRByte")[0]

	def IndGetSFRMem(self, addr, size):
		return self.rblk8(0x36, addr, size, "IndGetSFRMem")

	def IndSetSFRByte(self, addr, value):
		self.cmd(0x37, pack("BBB", addr, 1, value), err_msg="IndSetSFRByte")
	
	def IndSetSFRMem(self, addr, data):
		self.wblk8(0x37, addr, data, "IndSetSFRMem")
	
	def EraseUserSpace(self):
		tmo_save = self.rx_timeout
		self.rx_timeout = 15000
		try:
			self.cmd(0x3C, err_msg="EraseUserSpace")	
		finally:
			self.rx_timeout = tmo_save

	def MakeOTP(self):
		"""Unknown"""
		self.cmd(0x3D, err_msg="MakeOTP")

	def ClockStrobe(self, speed=1):
		self.cmd(0x40, pack('<B', speed), err_msg="ClockStrobe")

	def Detach(self):
		self.cmd(0x43, err_msg="Detach")
	
	def SetUSBPower(self, on=True):
		self.cmd(0xFE, pack('<B', 0 if on else 8))
				
	####################### high level functions #########################

	def connect(self):
		try:
			self.open()
			#TODO init device
			self.ResetAdapter()
			print("Reset OK")
			print("BL version:", self.BLGetVersion())
			print("OSX flag:", self.BLGetOSXFlag())
			try:
				self.BLSetPage(0x0C)
			except EC3Error as e:
				print(e)
			self.BLGo()
			self.ClockStrobe()
			self.Connect()
			self.IdentifyTarget()
			self.connected = True
		except:
			self.close()
			raise

	def disconnect(self):
		try:
			if self.connected:
				self.Disconnect()
				#self.ResetAdapter()
		finally:
			self.close()
			self.connected = False

##########################################################################

if __name__=="__main__":
	#ec3 = EC3(dump=True)
	ec3 = EC3()
	ec3.connect()
	print("Connect OK")
	print("Found hwid %02X, hwrev %02X, dlver %02X, derid %02X" % (ec3.HardwareID, ec3.HardwareRev, 
		ec3.DebugLogicVersion, ec3.DerivativeID))
	#ec3.IndSetSFRByte(0x8F, 0) # init PSCTL
	ec3.disconnect()
