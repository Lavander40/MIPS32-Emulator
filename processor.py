from exceptions import EmptyException

class EmulatorMIPS:
    # инициализация регистров, cmem, dmem и программного счётчика
    def __init__(self):
        # каждая ячейка равна машинному слову (32 бита)
        self.registers = [0] * 32
        self.instruction_memory = [0] * 256
        self.data_memory = [0] * 1024
        self.pc = 0

    # Старт выполнения программы
    def run(self):
        print(f"Starting command {self.pc}")
        # while True:
        print(f"\npc: {self.pc}")
        # получает операцию из массива команд
        instruction = self.fetch()
        if instruction == 0xFFFFFFFF:  # Команда остановки
            print("\nProgram finished (STOP command encountered)")
            raise EmptyException
            # break
        if instruction is None or instruction == 0x0:
            print("\nEmpty command encountered stopping the process")
            return
            # break
        print(hex(instruction))
        opcode, rs, rt, rd, imm = self.decode(instruction)
        self.execute(opcode, rs, rt, rd, imm)
        print(self.registers[:5])

    def execute(self, opcode, rs, rt, rd, imm):
        print("Command executing")
        if imm & 0x8000:  # Если старший бит 16-битного imm установлен
            imm |= 0xFFFF0000  # Расширяем старшие биты
            imm = imm - 0x100000000
        print(f"imm: {imm}")
        # Выполняет инструкцию в зависимости от старших битов
        match opcode:
            case 0x00:  # R-формат
                func = imm & 0x3F
                match func:
                    case 0x20:  # ADD
                        print("ADD")
                        res = self.registers[rs] + self.registers[rt]
                        # Проверка переполнения
                        if (self.registers[rs] > 0 > res and self.registers[rt] > 0) or \
                                (self.registers[rs] < 0 < res and self.registers[rt] < 0):
                            print("Overflow detected in ADD operation")
                        else:
                            self.registers[rd] = res
                    case 0x21:  # ADDU (сложение без учета переполнения)
                        print("ADDU")
                        self.registers[rd] = (self.registers[rs] + self.registers[rt]) & 0xFFFFFFFF
                    case 0x22:  # SUB
                        print("SUB")
                        res = self.registers[rs] - self.registers[rt]
                        # Проверка переполнения
                        if (self.registers[rs] > 0 > self.registers[rt] and res < 0) or \
                                (self.registers[rs] < 0 < self.registers[rt] and res > 0):
                            print("Overflow detected in SUB operation")
                        else:
                            self.registers[rd] = res
                    case 0x23:  # SUBU (вычитание без учета переполнения)
                        print("SUBU")
                        self.registers[rd] = (self.registers[rs] - self.registers[rt]) & 0xFFFFFFFF
                    case 0x24:  # AND
                        print("AND")
                        self.registers[rd] = self.registers[rs] & self.registers[rt]
                    case 0x25:  # OR
                        print("OR")
                        self.registers[rd] = self.registers[rs] | self.registers[rt]
                    case 0x26:  # XOR
                        print("XOR")
                        self.registers[rd] = self.registers[rs] ^ self.registers[rt]
                    case 0x27:  # NOR
                        print("NOR")
                        self.registers[rd] = ~(self.registers[rs] | self.registers[rt]) & 0xFFFFFFFF
                    case _:
                        raise ValueError(f"Неизвестная R-инструкция: {hex(func)}")
            case 0x02:  # безусловный переход
                print("J")
                target = imm & 0x3FFFFFF
                self.pc = target
            case 0x04:  # BEQ
                print("BEQ")
                if self.registers[rs] == self.registers[rt]:
                    imm = imm & 0xFFFF
                    self.pc += imm
            case 0x05:  # BNE
                print("BNE")
                if self.registers[rs] != self.registers[rt]:
                    self.pc += imm
            case 0x08:  # арифметика с непосредственным значением
                print("ADDI")
                result = self.registers[rs] + imm
                # Проверка переполнения
                if (self.registers[rs] > 0 > result and imm > 0) or \
                        (self.registers[rs] < 0 < result and imm < 0):
                    print("Overflow detected in ADDI operation")
                else:
                    self.registers[rt] = result
            case 0x09:  # ADDIU
                print("ADDIU")
                self.registers[rt] = self.registers[rs] + imm
                print(f"Result: {self.registers[rt]}")
            case 0x0C:  # ANDI
                print("ANDI")
                self.registers[rt] = self.registers[rs] & imm
                print(f"Result: {self.registers[rt]}")
            case 0x0D:  # ORI
                print("ORI")
                self.registers[rt] = self.registers[rs] | imm
                print(f"Result: {self.registers[rt]}")
            case 0x0E:  # XORI
                print("XORI")
                self.registers[rt] = self.registers[rs] ^ imm
                print(f"Result: {self.registers[rt]}")
            case 0x23:  # загрузка из памяти данных
                print("LW")
                address = (self.registers[rs] + imm)
                self.registers[rt] = self.data_memory[address]
                print(f"Loaded value: {self.registers[rt]} from address: {address * 4}")
            case 0x2B:  # сохранение в память данных
                print("SW")
                address = (self.registers[rs] + imm)
                self.data_memory[address] = self.registers[rt]
                print(f"Stored value: {self.registers[rt]} to address: {address * 4}")
            case _:
                raise ValueError(f"Неизвестная инструкция: {hex(opcode)}")

    # Загрузка программы в память команд
    def load_program(self, program):
        print("Start of incoming programm")
        self.pc = 0
        self.instruction_memory = [0] * 256
        for i, cmd in enumerate(program):
            if i < len(self.instruction_memory):
                self.instruction_memory[i] = cmd
                print(hex(cmd))
            else:
                print("Программа превышает размер командной памяти")
                return
        print("Program successfully loaded\n")

    # Извлекает текущую команду из памяти команд
    def fetch(self):
        if self.pc < len(self.instruction_memory):
            instruction = self.instruction_memory[self.pc]
            self.pc += 1
            return instruction
        return None

    # Декодирует 32-битную команду с трехадресной адресацией
    def decode(self, instruction):
        opcode = (instruction >> 26) & 0x3F  # Опкод (26-31 биты)
        rs = (instruction >> 21) & 0x1F  # Источник 1 (21-25 биты)
        rt = (instruction >> 16) & 0x1F  # Источник 2 (16-20 биты)
        rd = (instruction >> 11) & 0x1F  # Назначение (11-15 биты)
        imm = instruction & 0xFFFF  # Непосредственное значение для I-формата
        return opcode, rs, rt, rd, imm


# Инициализация
#emulator = EmulatorMIPS()
#disassembler = DisassemblerMIPS()

# Читаем ассемблерную программу
#program = disassembler.disassemble('program.asm')

# Пример программы для эмуляции (команды в виде 32-битных чисел)
# program = [
#     0x00221820,  # ADD R3, R1, R2 (R-формат)
#     0x00221822,  # SUB R3, R1, R2 (R-формат)
#     0x00221826,  # XOR R3, R1, R2 (R-формат)
#     0x20220004,  # ADDI R2, R1, 4 (I-формат)
#     0x30420005,  # ANDI R2, R2, 5 (I-формат)
#     0x38420001,  # XORI R2, R2, 1 (I-формат)
#     0xAC230000,  # SW R3, 0(R1)
#     0x8C230000,  # LW R3, 0(R1)
#     0xFFFFFFFF,  # STOP
# ]

# Инициализация регистров с произвольными значениями для теста
#emulator.registers[1] = 5
#emulator.registers[2] = 10

#emulator.load_program(program)  # Загружаем программу в память команд
#emulator.run()  # Запускаем выполнение программы
