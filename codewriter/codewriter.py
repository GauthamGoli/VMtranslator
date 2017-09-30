import os

class CodeWriter:
    def __init__(self, outputPath):
        self.writerObj = open(outputPath, 'a')
        self.unique_seq_key = 1
        self.currentFunction = None
        # Keeps track of number of function `call`s inside a function for generating labels accordingly
        self.currentFunctionCallIndex = None

    def setFileName(self, fileName):
        self.filename = os.path.basename(fileName).strip('.vm')

    def setCurrentFunction(self, functionName=None, functionCallIndex=None):
        self.currentFunction = functionName
        self.currentFunctionCallIndex = functionCallIndex

    def writeInit(self):
        command_seq = ['@256', 'D=A', '@SP', 'M=D']
        command_seq.append('// SP=256\n')
        self.writeLines(command_seq)
        self.setCurrentFunction('bootsrap', 0)
        self.writeCall('Sys.init', 0)
        self.setCurrentFunction()

    def writeLabel(self, label):
        if self.currentFunction is None:
            command_seq = ['({})'.format(label)]
        else:
            command_seq = ['({}${})'.format(self.currentFunction, label)]
        command_seq.append('// label decleration\n')
        self.writeLines(command_seq)

    def writeGoto(self, label):
        if self.currentFunction is None:
            command_seq = ['@{}'.format(label), '0;JMP']
        else:
            command_seq = ['@{}${}'.format(self.currentFunction, label) , '0;JMP']
        command_seq.append('//goto jmp\n')
        self.writeLines(command_seq)

    def writeIf(self, label):
        if self.currentFunction is None:
            labelName = label
        else:
            labelName = '{}${}'.format(self.currentFunction, label)
        command_seq = ['@SP', 'M=M-1','A=M', 'D=M', '@{}false'.format(labelName), 'D;JEQ', '@{}'.format(labelName), '0;JMP', '({}false)'.format(labelName)]
        command_seq.append('// if-goto jmp\n')
        self.writeLines(command_seq)

    def writeCall(self, functionName, nArgs):
        returnAddrLabelName = '{}$ret.{}'.format(self.currentFunction,
                                                 self.currentFunctionCallIndex)
        self.currentFunctionCallIndex += 1
        command_seq = ['@{}'.format(returnAddrLabelName), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] #push returnAddr
        command_seq += ['@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] #push LCL
        command_seq += ['@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] #push ARG
        command_seq += ['@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] #push THIS
        command_seq += ['@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] #push THAT
        command_seq += ['@SP', 'D=M','@5', 'D=D-A','@{}'.format(nArgs), 'D=D-A', '@ARG', 'M=D'] #ARG = SP-5-nArgs
        command_seq += ['@SP', 'D=M', '@LCL', 'M=D'] #LCL=SP
        command_seq += ['@{}'.format(functionName), '0;JMP'] #goto functionName
        command_seq += ['({})'.format(returnAddrLabelName)]
        command_seq.append('// writeCall \n')
        self.writeLines(command_seq)

    def writeFunction(self, functionName, nVars):
        self.setCurrentFunction(functionName, 0)
        self.returnAddrLabelName = '{}$ret.{}'.format(self.currentFunction, self.currentFunctionCallIndex)
        command_seq = ['({})'.format(functionName)]
        for x in range(nVars):
            command_seq += ['@SP', 'A=M', 'M=0', '@SP', 'M=M+1']
        command_seq.append('// writeFunction\n')
        self.writeLines(command_seq)

    def writeReturn(self):
        command_seq = ['@LCL', 'D=M', '@R14', 'M=D'] #R14(endFrame) = LCL
        command_seq += ['@R14', 'D=M', '@5', 'D=D-A','A=D', 'D=M', '@R13', 'M=D'] #returnAddr to R13
        command_seq += ['@SP', 'A=M-1', 'D=M', '@ARG', 'A=M', 'M=D'] #reposition return value for caller
        command_seq += ['@ARG', 'D=M+1', '@SP', 'M=D'] #reposition SP
        command_seq += ['@R14', 'A=M-1','D=M', '@THAT', 'M=D'] # reposition THAT
        command_seq += ['@R14', 'D=M', '@2', 'D=D-A','A=D','D=M', '@THIS', 'M=D'] #repostion THIS
        command_seq += ['@R14', 'D=M', '@3', 'D=D-A','A=D','D=M', '@ARG', 'M=D'] #reposition ARG
        command_seq += ['@R14', 'D=M', '@4', 'D=D-A','A=D','D=M', '@LCL', 'M=D'] #repostion LCL
        command_seq += ['@R13', 'A=M', '0;JMP'] # Goto returnAddr
        command_seq.append('// writeReturn\n')
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
        elif c_type in ['C_FUNCTION']:
            self.writeFunction(arg1, int(arg2) if arg2 else arg2)
        elif c_type in ['C_RETURN']:
            self.writeReturn()
        elif c_type in ['C_CALL']:
            self.writeCall(arg1, int(arg2) if arg2 else arg2)

        self.unique_seq_key += 1

    def writeLines(self, command_seq):
        self.writerObj.write('\n'.join(command_seq))

    def close(self):
        self.writerObj.close()