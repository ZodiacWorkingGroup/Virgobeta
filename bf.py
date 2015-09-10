import sys

class BF():
    def __init__(self, inputs = True, retout = False):
        self.code = None
        self.limit = 32767
        self.tape = [0]*(self.limit)
        self.pointer = 0
        self.loopcount = 0
        self.inputtable = inputs
        self.returnoutput = retout
        self.outpstr = ""

    def gt(self):
        if self.pointer >= self.limit:
            return -1
        else:
            self.pointer += 1
            return 0

    def lt(self):
        if self.pointer <= 0:
            return -1
        else:
            self.pointer -= 1
            return 0

    def plus(self):
        self.tape[self.pointer] = (self.tape[self.pointer] + 1) % 256
        return 0

    def minus(self):
        self.tape[self.pointer] = (self.tape[self.pointer] - 1) % 256
        return 0

    def dot(self):
        if self.returnoutput:
            self.outpstr += chr(self.tape[self.pointer])
        else:
            sys.stdout.write(chr(self.tape[self.pointer]))
        return 0

    def comma(self):
        if self.inputtable:
            self.tape[self.pointer] = ord(sys.stdin.read(1))
            return 0
        else:
            return -1024

    handles = {".":dot,",":comma,"<":lt,">":gt,"+":plus,"-":minus}

    def apply(self, func):
        ret = func(self)
        if ret != 0:
            return -(4096+(-ret))
        else:
            return 0

    def parse(self, code):
        opening = []
        loop = {}
        for i,c in enumerate(code):
            if c == "[":
                opening.append(i)
            elif c == "]":
                try:
                    begin = opening.pop()
                    loop[begin] = i
                except IndexError:
                    return -3
                except:
                    return -1
        if opening != []:
            return -2
        else:
            return loop

    def evaluate(self, code):
        self.reset()
        self.code = code
        loop = self.parse(self.code)
        pc = 0
        stack = []
        while pc < len(self.code):
            instruction = self.code[pc]
            if instruction in self.handles:
                self.loopcount += 1
                if self.loopcount >= 8192:
                    return -8192
                else:
                    rt = self.apply(self.handles[instruction])
            elif instruction == "[":
                if self.tape[self.pointer] > 0:
                    stack.append(pc)
                else:
                    pc = loop[pc]
            elif instruction == "]":
                pc = stack.pop() - 1
            pc += 1
        if self.returnoutput:
            return self.outpstr
        else:
            pass
        

    def reset(self):
        self.code = None
        self.limit = 32767
        self.tape = [0]*(self.limit)
        self.pointer = 0
        self.loopcount = 0
