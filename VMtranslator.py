import os
import sys
import glob
from codewriter.codewriter import CodeWriter
from parser.parser import Parser

if(len(sys.argv)<2):
	print "Supply file/dir location."
	sys.exit()
else:
	input_path = os.path.abspath(sys.argv[1])
	vm_files = glob.glob(input_path+'/*.vm') if os.path.isdir(input_path) else [input_path]
	for vm_file in vm_files:
		parser = Parser(vm_file)
		output_path = vm_file.replace('.vm', '.asm')
		writer = CodeWriter(output_path)
		writer.setFileName(input_path)
		while(parser.hasMoreCommands()):
			parser.advance()
			writer.writeCommand(parser.commandType(), parser.arg1(), parser.arg2())
		writer.close()
		print "Translation finished"
