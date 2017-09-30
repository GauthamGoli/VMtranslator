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
	output_path = os.path.join(os.path.join(os.path.dirname(input_path), os.path.basename(input_path)), os.path.basename(input_path)+'.asm') if os.path.isdir(input_path) else input_path.replace('.vm', '.asm')
	writer = CodeWriter(output_path)
	if os.path.join(input_path,'Sys.vm') in vm_files:
		vm_files.remove(os.path.join(input_path,'Sys.vm'))
		vm_files.insert(0, os.path.join(input_path,'Sys.vm'))
		writer.writeInit()
	for vm_file in vm_files:
		parser = Parser(vm_file)
		writer.setFileName(vm_file)
		while(parser.hasMoreCommands()):
			parser.advance()
			writer.writeCommand(parser.commandType(), parser.arg1(), parser.arg2())
		print "Translation finished"
	writer.close()
