import os
import time

class CodeWriter:
    def __init__(self, outputPath):
        self.writerObj = open(outputPath, 'a')
        self.filename = os.path.basename(outputPath)

    def writePushPop(self, command, segment, index):
        segment_names = {
                            'local'   : 'LCL',
                            'argument': 'ARG',
                            'this'    : 'THIS',
                            'that'    : 'THAT'
                       }

        if command == 'C_POP':
            if segment in ['local', 'argument', 'this',' that']:
                segment_pointer = segment_name[segment]
                command_seq = ['@{}'.format(index), 'D=A', '@{}'.format(segment_pointer), 'D=D+M', '@SP', 'M=M-1','A=M','M=D'] 
            elif segment == 'static':
                command_seq = ['@SP', 'M=M-1', 'A=M', 'D=A', '@{}.{}'.format(self.filename, index), 'M=D']
            elif segment == 'temp':
                command_seq = ['@{}'.format(index), 'D=A', '@5', 'D=D+A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
            elif segment == 'this':
                if index == 0:
                    pointer = 'THIS'
                else:
                    pointer = 'THAT'
                command_seq = ['@SP', 'M=M-1', 'A=M', 'D=M', '@{}'.format(pointer), 'A=M', 'M=D']

            command_seq.append('// POP {} {}\n'.format(semgent, index))
            self.writeLines(command_seq)

        elif command == 'C_PUSH':
            if segment == 'constant':
                command_seq = ['@{}'.format(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
                command_seq.append('// PUSH CONST {}\n'.format(index))
            elif segment == 'temp':
                command_seq = ['@{}'.format(index), 'D=A', '@5', 'D=D+A', '@SP', 'M=M-1', 'A=M', 'M=D']
            elif segment == 'this':
                if index == 0:
                    pointer = 'THIS'
                else:
                    pointer = 'THAT'
                command_seq = ['@SP', 'A=M', 'M={}'.format(pointer), '@SP', 'M+1']

            command_seq.append('// PUSH {} {}\n'.format(semgent, index))
            self.writeLines(command_seq)

    def writeArithmetic(self, command):
        if command == 'add':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D+M','M=D']
        elif command == 'sub':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D-M','M=D']
        elif command == 'neg':
            command_seq = ['@SP','D=M-1','A=D','M=-M']
        elif command == 'eq':
            command_seq = ['@SP','M=M-1','A=M', 'D=M', '@SP', 'M=M-1', 'A=M', 'D=D-M','M=!D','D=0', 'D=!D', 'M=D&M', '@SP', 'M=M+1']
        elif command == 'and':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D&M','M=D', '@SP','M=M+1']
        elif command == 'or':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D!M','M=D', '@SP','M=M+1']
        elif command == 'not':
            command_seq = ['@SP','M=M-1','A=M','M=!M','@SP','M=M+1']
        elif command == 'lt':
            unique_label = int(time.time())
            command_seq = ['@SP', 'M=M-1','A=M','D=M','@SP','M=M-1','A=M','@lt{}lt'.format(unique_label),'D=D-M;JLT','@nlt{}nlt'.format(unique_label),'0;JMP','(lt{}lt)'.format(unique_label),'@SP','A=M','D=0','M=!D','(nlt{}nlt)'.format(unique_label),'@SP','A=M','D=1','M=!D']
        elif command == 'gt':
            unique_label = int(time.time())
            command_seq = ['@SP', 'M=M-1','A=M','D=M','@SP','M=M-1','A=M','@gt{}gt'.format(unique_label),'D=D-M;JGT','@ngt{}ngt'.format(unique_label),'0;JMP','(gt{}gt)'.format(unique_label),'@SP','A=M','D=0','M=!D','(ngt{}ngt)'.format(unique_label),'@SP','A=M','D=1','M=!D']

        command_seq.append('// {}\n'.format(command))
        self.writeLines(command_seq)

    def writeCommand(self, type, arg1, arg2)
        if type in ['C_PUSH','C_POP']:
            self.writePushPop(type, arg1, arg2)
        elif type in ['C_ARITHMETIC']:
            self.writeArithmetic(arg1)

    def writeLines(self, command_seq):
        self.writeObj.write(command_seq.join('\n'))

    def close(self):
        self.writerObj.close()