class Parser:
    def __init__(self, filepath):
        file_pointer = open(filepath)
        self.lines = file_pointer.readlines()
        self.lines.reverse()

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
        # Incomplete
        self.currentCommand = self.currentCommand.index('//')

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

    def arg1(self):
        if self.commandType() == 'C_ARITHMETIC':
            return self.command_tokens[0] 
        elif self.commandType() in ['C_PUSH','C_POP','C_LABEL','C_GOTO','C_IFGOTO']:
            return self.command_tokens[1]

    def arg2(self):
        if self.commandType() in ['C_PUSH', 'C_POP']:
            return self.command_tokens[2]
        else:
            return None

