"""CPU functionality."""

import sys

LDI = 0b10000010 # LDI
PRN = 0b01000111 # PRN
MUL = 0b10100010 # MUL
PUSH = 0b01000101 # PUSH
POP = 0b01000110 # POP
HLT = 0b00000001 # HALT
CALL = 0b01010000 # CALL
RET = 0b00010001 # RET
ADD = 0b10100000 # ADD
CMP = 0b10100111 # CMP
JMP  = 0b01010100 # JMP
JEQ  = 0b01010101 # JEQ
JNE  = 0b01010110 # JNE

if len(sys.argv) < 2:
    sys.exit(1)

class CPU:
    """Main CPU class."""

    def __init__(self, reg = [0] * 8, ram = [0] * 256, pc = 0):
        """Construct a new CPU."""
        self.reg = reg
        self.ram = ram
        self.pc = pc
        self.sp = self.reg[7]
        self.fl = [0] * 8
        self.running = True 

        #branchtable
        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            MUL: self.mul,
            ADD: self.add,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            CMP: self.compare,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne
        }

    def load(self):
        """Load a program into memory."""

        program = []
        address = 0

        with open(sys.argv[1]) as f:
            for line in f:
                l = line.split('#')
                operation = l[0].strip()
                try:
                    program.append(int(operation, 2))
                except ValueError:
                    pass

        for operation in program:
            self.ram[address] = operation
            address += 1

    def add(self, op_1, op_2):
        self.reg[self.ram[self.pc + 1]] += self.reg[self.ram[self.pc + 2]]

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
          pass

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, register):
        return self.ram[register]

    def ram_write(self, register, address):
        self.ram[address] = register

    def hlt(self, op_1, op_2):
        self.running = False

    def call(self, op_1, op_2):
        next_address = self.pc + 2
        self.sp -= 1
        self.ram[self.sp] = next_address

        address = self.reg[self.ram[self.pc + 1]]
        self.pc = address

    def ret(self, op_1, op_2):
        next_address = self.ram[self.sp]
        self.sp += 1

        self.pc = next_address

    def ldi(self, address, value):
        self.reg[address] = value

    def prn(self, address, op_2):
        print(self.reg[address])

    def mul(self, op_1, op_2):
        self.alu("MUL", op_1, op_2)

    def run(self, op_1, op_2):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            op_1 = self.ram_read(self.pc + 1)
            op_2 = self.ram_read(self.pc + 2)

            op_size = ir >> 6
            mask = ((ir >> 4) & 0b1) == 1

            if ir in self.branchtable:
                self.branchtable[ir](op_1, op_2)
            else:
                exit()
            if mask == False:
                self.pc += op_size + 1

    def push(self, op_1, op_2):
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = self.reg[op_1]

    def pop(self, op_1, op_2):
        sp = self.reg[7]       
        value = self.ram[sp]
        self.reg[op_1] = value

    def compare(self, op_1, op_2):
      value1 = self.reg[op_1]
      value2 = self.reg[op_2]
      if value1 < value2:
          self.fl[5] = 1
      elif value1 > value2:
          self.fl[6] = 1
      elif value1 == value2:
          self.fl[7] = 1
      else: 
          pass

    def jmp(self, address, op_2):
        self.pc = self.reg[address]

    def jeq(self, op_1, op_2):
        if self.fl[7] == 1:
            self.jmp(op_1, op_2)
        else:
            self.pc += 2

    def jne(self, op_1, op_2):
      if self.fl[7] == 0:
          self.jmp(op_1, op_2)
      else:
          self.pc += 2