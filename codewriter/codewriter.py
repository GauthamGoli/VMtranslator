import os

class CodeWriter:
    def __init__(self, outputPath):
        self.writerObj = open(outputPath, 'a')
        self.unique_seq_key = 1

    def setFileName(self, fileName):
        self.filename = os.path.basename(fileName)

    def writeLabel(self, label):
        command_seq = ['({})'.format(label)]
        command_seq.append('// label decleration\n')
        self.writeLines(command_seq)

    def writeGoto(self, label):
        command_seq = ['@{}'.format(label), '0;JMP']
        command_seq.append('//goto jmp\n')
        self.writeLines(command_seq)

    def writeIf(self, label):
        command_seq = ['@SP', 'M=M-1','A=M', 'D=M', '@{}false'.format(label), 'D;JEQ', '@{}'.format(label), '0;JMP', '({}false)'.format(label)]
        command_seq.append('// if-goto jmp\n')
        self.writeLines(command_seq)

    def writePushPop(self, command, segment, index):
        segment_names = {
                            'local'   : 'LCL',
                            'argument': 'ARG',
                            'this'    : 'THIS',
                            'that'    : 'THAT'
                       }

        if command == 'C_POP':
            if segment in ['local', 'argument', 'this','that']:
                segment_pointer = segment_names[segment]
                command_seq = ['@{}'.format(index), 'D=A', '@{}'.format(segment_pointer), 'D=D+M', '@R13','M=D', '@SP', 'M=M-1','A=M','D=M','@R13', 'A=M','M=D']
            elif segment == 'static':
                command_seq = ['@SP', 'M=M-1', 'A=M', 'D=M', '@{}.{}'.format(self.filename, index), 'M=D']
            elif segment == 'temp':
                command_seq = ['@{}'.format(index), 'D=A', '@5', 'D=D+A', '@R13', 'M=D', '@SP','M=M-1', 'A=M', 'D=M','@R13','A=M','M=D']
            elif segment == 'pointer':
                if index == '0':
                    pointer = 'THIS'
                else:
                    pointer = 'THAT'
                command_seq = ['@SP', 'M=M-1', 'A=M', 'D=M', '@{}'.format(pointer), 'M=D']

            command_seq.append('// POP {} {}\n'.format(segment, index))
            self.writeLines(command_seq)

        elif command == 'C_PUSH':
            if segment in ['local', 'argument', 'this', 'that']:
                segment_pointer = segment_names[segment]
                command_seq = ['@{}'.format(index), 'D=A', '@{}'.format(segment_pointer), 'D=D+M','A=D','D=M', '@SP', 'A=M','M=D','@SP','M=M+1']
            elif segment == 'static':
                command_seq = ['@{}.{}'.format(self.filename, index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
            elif segment == 'constant':
                command_seq = ['@{}'.format(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
            elif segment == 'temp':
                command_seq = ['@{}'.format(index), 'D=A', '@5', 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
            elif segment == 'pointer':
                if index == '0':
                    pointer = 'THIS'
                else:
                    pointer = 'THAT'
                command_seq = ['@{}'.format(pointer), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

            command_seq.append('// PUSH {} {}\n'.format(segment, index))
            self.writeLines(command_seq)

    def writeArithmetic(self, command):
        unique_label = self.unique_seq_key
        if command == 'add':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','M=D+M', '@SP', 'M=M+1']
        elif command == 'sub':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','M=M-D', '@SP', 'M=M+1']
        elif command == 'neg':
            command_seq = ['@SP','A=M-1','M=-M']
        elif command == 'eq':
            command_seq = ['@SP','M=M-1','A=M', 'D=M', '@SP', 'M=M-1', 'A=M','D=D-M', '@eq{}eq'.format(unique_label), 'D;JEQ', '@SP','A=M','M=0', '@neq{}neq'.format(unique_label), '0;JMP','(eq{}eq)'.format(unique_label),'@SP', 'A=M', 'M=-1','(neq{}neq)'.format(unique_label), '@SP', 'M=M+1']
        elif command == 'and':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D&M','M=D', '@SP','M=M+1']
        elif command == 'or':
            command_seq = ['@SP','M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=D|M','M=D', '@SP','M=M+1']
        elif command == 'not':
            command_seq = ['@SP','M=M-1','A=M','M=!M','@SP','M=M+1']
        elif command == 'lt':
            command_seq = ['@SP', 'M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=M-D', '@lt{}lt'.format(unique_label),'D;JLT','@SP', 'A=M', 'M=0', '@nlt{}nlt'.format(unique_label),'0;JMP','(lt{}lt)'.format(unique_label),'@SP','A=M','M=-1', '(nlt{}nlt)'.format(unique_label),'@SP','M=M+1']
        elif command == 'gt':
            command_seq = ['@SP', 'M=M-1','A=M','D=M','@SP','M=M-1','A=M','D=M-D', '@gt{}gt'.format(unique_label),'D;JGT','@SP', 'A=M', 'M=0', '@ngt{}ngt'.format(unique_label),'0;JMP','(gt{}gt)'.format(unique_label),'@SP','A=M','M=-1', '(ngt{}ngt)'.format(unique_label),'@SP','M=M+1']

        command_seq.append('// {}\n'.format(command))
        self.writeLines(command_seq)

    def writeCommand(self, c_type, arg1, arg2):
        if c_type in ['C_PUSH','C_POP']:
            self.writePushPop(c_type, arg1, arg2)
        elif c_type in ['C_ARITHMETIC']:
            self.writeArithmetic(arg1)
        elif c_type in ['C_LABEL']:
            self.writeLabel(arg1)
        elif c_type in ['C_GOTO']:
            self.writeGoto(arg1)
        elif c_type in ['C_IFGOTO']:
            self.writeIf(arg1)

        self.unique_seq_key += 1

    def writeLines(self, command_seq):
        self.writerObj.write('\n'.join(command_seq))

    def close(self):
        self.writerObj.close()