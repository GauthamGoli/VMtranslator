class Parser:
    def __init__(self, filepath):
        file_pointer = open(filepath)
        self.lines = file_pointer.readlines()
        self.lines.reverse()
        self.strip_comments()

    def hasMoreCommands(self):
        return len(self.lines)>0

    def advance(self):
        if(self.hasMoreCommands()):
            self.currentCommand = self.lines.pop()
            self.tokenize()
        return

    def tokenize(self):
        self.command_tokens = self.currentCommand.strip().split()

    def strip_comments(self):
        strippedLines = []
        for line in self.lines[:]:
            try:
                strippedLines.append(line[:line.index('//')].rstrip())
            except:
                strippedLines.append(line.strip())
        self.lines = [line for line in strippedLines if line]

    def commandType(self):
        try:
            operation = self.command_tokens[0]
        except:
            return None

        if operation in ['add','sub', 'neg', 'eq','gt','lt','and','or','not' ]:
            return 'C_ARITHMETIC'
        elif operation == 'push':
            return 'C_PUSH'
        elif operation == 'pop':
            return 'C_POP'
        elif operation == 'label':
            return 'C_LABEL'
        elif operation == 'goto':
            return 'C_GOTO'
        elif operation == 'if-goto':
            return 'C_IFGOTO'
        elif operation == 'function':
            return 'C_FUNCTION'
        elif operation == 'call':
            return 'C_CALL'
        elif operation == 'return':
            return 'C_RETURN'

    def arg1(self):
        if self.commandType() in ['C_ARITHMETIC', 'C_RETURN']:
            return self.command_tokens[0] 
        elif self.commandType() in ['C_PUSH','C_POP','C_LABEL','C_GOTO','C_IFGOTO', 'C_FUNCTION', 'C_CALL']:
            return self.command_tokens[1]

    def arg2(self):
        if self.commandType() in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']:
            return self.command_tokens[2]
        else:
            return None

