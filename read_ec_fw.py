#!/usr/bin/python3

from struct import pack
from ec3 import EC3

def dump_fw(fname, start, size):
	ec3 = EC3()
	ec3.open()
	ec3.ResetAdapter()
	print("Connect OK")

	hfo = open(fname, "wb")
	for addr in range(start, start+size):
		hfo.write(pack('<B', ec3.BLReadByte(addr)))
	hfo.close()

	ec3.close()
	return True
	
dump_fw("ec3_fw.bin", 0, 0x3E00)
