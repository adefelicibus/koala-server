# -*- coding: utf-8 -*-
"""
XML format classes
"""
import data
import logging
from galaxy.datatypes.sniff import *
import commands

log = logging.getLogger(__name__)


class ini( data.Text ):
	file_ext = "ini"
	def sniff( self, filename ):
		self.no_sections = commands.getstatusoutput("grep -c \"\[Docking-Settings\]\" "+filename)
		if (self.no_sections[0] == 0) & (self.no_sections[1] > 0):
			return True
		else:
			self.no_sections = commands.getstatusoutput("grep -c \"\[ReferenceArea\" "+filename)
			if (self.no_sections[0] == 0) & (self.no_sections[1] > 0):
				return True
			else:
				self.no_sections = commands.getstatusoutput("grep -c \"\[PharmacophoreConstraint\" "+filename)
				if (self.no_sections[0] == 0) & (self.no_sections[1] > 0):
					return True
				else:
					return False




