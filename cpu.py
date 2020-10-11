"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = {
            '0b00000000': None,
            '0b00000001': None,
            '0b00000010': None,
            '0b00000011': None,
            '0b00000100': None,
            '0b00000101': None,
            '0b00000110': None,
            '0b00000111': None
        }
        self.stack = []
        self.pc = 0
        self.SP = 0
        self.IR = None  
        self.MAR = None
        self.MDR = None
        self.FL = 0b000
        self.running = False
        self.alu_codes = {
            '0b10100000': "ADD",
            '0b10100001': "SUB",
            '0b10100010': "MUL",
            '0b10100011': "DIV",
            '0b10100100': "MOD",
            '0b01100101': "INC",
            '0b01100110': "DEC",
            '0b10100111': "CMP",
            '0b10101000': "AND",
            '0b01101001': "NOT",
            '0b10101010': "OR",
            '0b10101011': "XOR",
            '0b10101100': "SHL",
            '0b10101101': "SHR"
        }
        self.pc_codes = {
            '0b01010000': "CALL",
            '0b00010001': "RET",
            '0b01010010': "INT",
            '0b00010011': "IRET",
            '0b01010100': "JMP",
            '0b01010101': "JEQ",
            '0b01010110': "JGT",
            '0b01011000': "JLT",
            '0b01011001': "JLE",
            '0b01011010': "JGE",
            '0b01010110': "JNE"
        }
        self.other_codes = {
            '0b00000000': "NOP",
            '0b00000001': "HLT",
            '0b10000010': "LDI",
            '0b10000011': "LD",
            '0b10000100': "ST",
            '0b01000101': "PUSH",
            '0b01000110': "POP",
            '0b01000111': "PRN",
            '0b01001000': "PRA"
        }

    def load(self, program):
        """Load a program into memory."""

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, byte):
        instructions = []
        info = byte[2:]
        operands = int(info[0:2], 2)
        alu = int(info[2:3], 2)
        pc = int(info[3:4], 2)
        ops = []
        if operands > 0:
            for i in range(1,operands+1):
                ops.append(self.ram[self.pc + i])
        if alu:
            instructions.append("ALU")
            instructions.append(self.alu_codes[byte])
        elif pc:
            instructions.append("PC")
            instructions.append(self.pc_codes[byte])
        else:
            instructions.append("OTHER")
            instructions.append(self.other_codes[byte])
        self.pc += (operands + 1)
        instructions.append(ops)
        
        return instructions

    def ram_write(self):
        pass

    def alu(self, op, args):
        """ALU operations."""
        reg_a = args[0]
        if len(args) == 2:
            reg_b = args[1]

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            if self.reg[reg_b] == 0:
                self.ot_op('HLT')
            else:
                self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b001
        elif op == "AND":
            self.reg[reg_a] = reg_a & self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] = (self.reg[reg_b] << int(self.reg[reg_b],2))
        elif op == "SHR":
            self.reg[reg_a] = (self.reg[reg_b] >> int(self.reg[reg_b],2))
        else:
            raise Exception("Unsupported ALU operation")

    def pc_op(self, command, args):
        if command == 'CALL':
            self.ot_op('PUSH')
            self.pc = self.reg[args[0]]
        if command == 'RET':
            self.pc = self.ot_op('POP')
            self.ram[self.SP] = 0
            self.SP += 1
        if command == 'JMP':
            self.pc = self.reg[args[0]]
        if command == 'JEQ':
            if self.FL == 4:
                self.pc_op('JMP', args)
        if command == 'JGE':
            if self.FL == 4 or self.FL == 2:
                self.pc_op('JMP', args)
        if command == 'JGT':
            if self.FL == 2:
                self.pc_op('JMP', args)
        if command == 'JLE':
            if self.FL == 4 or self.FL == 1:
                self.pc_op('JMP', args)
        if command == 'JLT':
            if self.FL == 1:
                self.pc_op('JMP', args)
        if command == 'JNE':
            if self.FL & 0b100 == 0:
                self.pc_op('JMP', args)

    def ot_op(self, command, args=None):
        if command == 'PRN':
            print(self.reg[args[0]])
        if command == 'LDI':
            self.reg[args[0]] = int(args[1][2:],2)
        if command == 'LD':
            self.reg[args[0]] = self.reg[args[1]]
        if command == 'HLT':
            self.running = False
        if command == 'PUSH':
            if args != None:
                self.SP -= 1
                self.ram[self.SP] = self.reg[args[0]]
            else:
                self.SP -= 1
                self.ram[self.SP] = self.pc
        if command == 'POP':
            if args is not None:
                self.reg[args[0]] = self.ram[self.SP]
            else:
                return self.ram[self.SP]
            self.ram[self.SP] = 0
            self.SP += 1
        if command == 'PRA':
            print("PRA CALLED",self.pc)
            # print(chr(int(self.reg[args[0]],2)))
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

    def run(self):
        self.running = True
        while self.running:
            self.IR = self.ram_read(self.ram[self.pc])

            if len(self.IR) == 3:
                command = self.IR[1]
                args = self.IR[2]
            else:
                command = self.IR[1]
                args = None

            if self.IR[0] == "ALU":
                self.alu(command, args)
            elif self.IR[0] == "PC":
                self.pc_op(command, args)
            elif self.IR[0] == "OTHER":
                self.ot_op(command, args)