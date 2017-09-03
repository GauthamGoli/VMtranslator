import os
import sys
from codewriter.codewriter import CodeWriter
from parser.parser import Parser

if(len(sys.argv)<2):
	print "Supply file location."
	sys.exit()
else:
	input_path = os.path.abspath(sys.argv[1])
	parser = Parser(input_path)
	output_path = input_path.replace('.vm', '.asm')
	writer = CodeWriter(output_path)
	while(parser.hasMoreCommands()):
		parser.advance()
		writer.writeCommand(parser.commandType(), parser.arg1(), parser.arg2())
	writer.close()
	print "Translation finished"
