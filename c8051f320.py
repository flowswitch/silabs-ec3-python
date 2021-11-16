"""Silabs C8051F32x constants"""

__all__ = ["SFRS"]

# SFRs
class SFRS(object):
	sfrs = { "P0" : 0x80,
	"SP" : 0x81,
	"DPL" : 0x82,
	"DPH" : 0x83,
	"PCON" : 0x87,
	"TCON" : 0x88,
	"TMOD" : 0x89,
	"TL0" : 0x8A,
	"TL1" : 0x8B,
	"TH0" : 0x8C,
	"TH1" : 0x8D,
	"CKCON" : 0x8E,
	"PSCTL" : 0x8F,
	"P1" : 0x90,
	"TMR3CN" : 0x91,
	"TMR3RLL" : 0x92,
	"TMR3RLH" : 0x93,
	"TMR3L" : 0x94,
	"TMR3H" : 0x95,
	"USB0ADR" : 0x96,
	"USB0DAT" : 0x97,
	"SCON0" : 0x98,
	"SBUF0" : 0x99,
	"CPT1CN" : 0x9A,
	"CPT0CN" : 0x9B,
	"CPT1MD" : 0x9C,
	"CPT0MD" : 0x9D,
	"CPT1MX" : 0x9E,
	"CPT0MX" : 0x9F,
	"P2" : 0xA0,
	"SPICFG" : 0xA1,
	"SPI0CFG" : 0xA1,
	"SPICKR" : 0xA2,
	"SPI0CKR" : 0xA2,
	"SPIDAT" : 0xA3,
	"SPI0DAT" : 0xA3,
	"P0MDOUT" : 0xA4,
	"P1MDOUT" : 0xA5,
	"P2MDOUT" : 0xA6,
	"P3MDOUT" : 0xA7,
	"IE" : 0xA8,
	"CLKSEL" : 0xA9,
	"EMI0CN" : 0xAA,
	"P3" : 0xB0,
	"OSCXCN" : 0xB1,
	"OSCICN" : 0xB2,
	"OSCICL" : 0xB3,
	"FLSCL" : 0xB6,
	"FLKEY" : 0xB7,
	"IP" : 0xB8,
	"CLKMUL" : 0xB9,
	"AMX0N" : 0xBA,
	"AMX0P" : 0xBB,
	"ADC0CF" : 0xBC,
	"ADC0L" : 0xBD,
	"ADC0H" : 0xBE,
	"SMB0CN" : 0xC0,
	"SMB0CF" : 0xC1,
	"SMB0DAT" : 0xC2,
	"ADC0GTL" : 0xC3,
	"ADC0GTH" : 0xC4,
	"ADC0LTL" : 0xC5,
	"ADC0LTH" : 0xC6,
	"TMR2CN" : 0xC8,
	"REG0CN" : 0xC9,
	"TMR2RLL" : 0xCA,
	"TMR2RLH" : 0xCB,
	"TMR2L" : 0xCC,
	"TMR2H" : 0xCD,
	"PSW" : 0xD0,
	"REF0CN" : 0xD1,
	"P0SKIP" : 0xD4,
	"P1SKIP" : 0xD5,
	"P2SKIP" : 0xD6,
	"USB0XCN" : 0xD7,
	"PCA0CN" : 0xD8,
	"PCA0MD" : 0xD9,
	"PCA0CPM0" : 0xDA,
	"PCA0CPM1" : 0xDB,
	"PCA0CPM2" : 0xDC,
	"PCA0CPM3" : 0xDD,
	"PCA0CPM4" : 0xDE,
	"ACC" : 0xE0,
	"XBR0" : 0xE1,
	"XBR1" : 0xE2,
	"IT01CF" : 0xE4,
	"EIE1" : 0xE6,
	"EIE2" : 0xE7,
	"ADC0CN" : 0xE8,
	"PCA0CPL1" : 0xE9,
	"PCA0CPH1" : 0xEA,
	"PCA0CPL2" : 0xEB,
	"PCA0CPH2" : 0xEC,
	"PCA0CPL3" : 0xED,
	"PCA0CPH3" : 0xEE,
	"RSTSRC" : 0xEF,
	"B" : 0xF0,
	"P0MDIN" : 0xF1,
	"P1MDIN" : 0xF2,
	"P2MDIN" : 0xF3,
	"P3MDIN" : 0xF4,
	"EIP1" : 0xF6,
	"EIP2" : 0xF7,
	"SPI0CN" : 0xF8,
	"PCA0L" : 0xF9,
	"PCA0H" : 0xFA,
	"PCA0CPL0" : 0xFB,
	"PCA0CPH0" : 0xFC,
	"PCA0CPL4" : 0xFD,
	"PCA0CPH4" : 0xFE,
	"VDM0CN" : 0xFF}

	def __init__(self, port):
		self.port = port

	def __getattribute__(self, attr):
		if attr in ("__dict__", "port", "sfrs") or not attr in self.sfrs:
			return object.__getattribute__(self, attr)
		val = self.port.GetSFRByte(self.sfrs[attr])
		#print("Get SFR %s = %02X" % (attr, val))
		return val

	def __setattr__(self, attr, value):
		if attr in self.__dict__ or attr=="port":
			object.__setattr__(self, attr, value)
			return
		if attr in self.sfrs:
			#print("Set SFR %s = %02X" % (attr, value))
			self.port.SetSFRByte(self.sfrs[attr], value)
			return 
		raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, attr))

