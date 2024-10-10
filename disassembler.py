import re

class DisassemblerMIPS:
    def __init__(self):
        self.opcode_map = {
            'ADD': 0x00,
            'SUB': 0x00,
            'ADDU': 0x00,
            'SUBU': 0x00,
            'AND': 0x00,
            'OR': 0x00,
            'XOR': 0x00,
            'NOR': 0x00,
            'J': 0x02,
            'BEQ': 0x04,
            'BNE': 0x05,
            'ADDI': 0x08,
            'ADDIU': 0x09,
            'ANDI': 0x0C,
            'ORI': 0x0D,
            'XORI': 0x0E,
            'LW': 0x23,
            'SW': 0x2B,
        }
        self.funct_map = {
            'ADD': 0x20,
            'ADDU': 0x21,
            'SUB': 0x22,
            'SUBU': 0x23,
            'AND': 0x24,
            'OR': 0x25,
            'XOR': 0x26,
            'NOR': 0x27,
        }
        self.labels = {}  # Таблица меток

    def disassemble(self, asm_code):
        program = []
        lines = asm_code.splitlines()  # Разбиваем текст на строки

        # Проход 1: Собираем метки
        pc = 0  # Программный счетчик
        for line in lines:
            line = line.strip()
            if line.endswith(':'):  # Если строка заканчивается на двоеточие — это метка
                label = line[:-1]
                self.labels[label] = pc  # Запоминаем адрес метки
            else:
                pc += 1  # Увеличиваем программный счётчик для каждой инструкции

        # Проход 2: Преобразуем команды в машинный код
        pc = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.endswith(':'):
                program.append(0)
                pc += 1
                continue
            try:
                machine_code = self.assemble_instruction(line, pc)  # Преобразуем строку в машинный код
                program.append(machine_code)
                pc += 1
            except ValueError as e:
                print(f"Ошибка обработки строки '{line}': {e}")
        program.append(4294967295)
        return program

    def assemble_instruction(self, line, pc):
        parts = line.split()
        instr = parts[0]

        if instr in self.funct_map:  # R-формат
            rd = self.parse_register(parts[1].strip(','))
            rs = self.parse_register(parts[2].strip(','))
            rt = self.parse_register(parts[3])
            opcode = self.opcode_map[instr] << 26
            funct = self.funct_map[instr]
            machine_code = (opcode | (rs << 21) | (rt << 16) | (rd << 11) | funct)
            return machine_code

        elif instr in self.opcode_map:
            if instr in ['LW', 'SW']:
                rt = self.parse_register(parts[1].strip(','))
                offset, base_register = self.parse_memory_address(parts[2])
                if offset < 0:
                    offset = (1 << 16) + offset
                opcode = self.opcode_map[instr] << 26
                machine_code = (opcode | (base_register << 21) | (rt << 16) | (offset & 0xFFFF))
                return machine_code
            else:  # I-формат
                rt = self.parse_register(parts[1].strip(','))
                rs = self.parse_register(parts[2].strip(','))

                # Поддержка меток для команд с переходами
                if instr in ['BEQ', 'BNE']:
                    imm = self.resolve_label(parts[3], pc)
                else:
                    imm = int(parts[3])

                imm = self.check_immediate(imm, bits=16)  # Проверка размера значения
                opcode = self.opcode_map[instr] << 26
                machine_code = (opcode | (rs << 21) | (rt << 16) | (imm & 0xFFFF))
                return machine_code
        else:
            raise ValueError(f"Неизвестная инструкция: {instr}")

    # Метод для преобразования метки в адрес
    def resolve_label(self, label, pc):
        if label in self.labels:
            target_pc = self.labels[label]
            offset = target_pc - pc + 1
            return offset
        else:
            raise ValueError(f"Метка '{label}' не найдена")

    def parse_register(self, reg_str):
        if reg_str[0] != 'R' or not reg_str[1:].isdigit():
            raise ValueError(f"Некорректный регистр: {reg_str}")
        reg_num = int(reg_str[1:])
        if not (0 <= reg_num < 32):
            raise ValueError(f"Регистр {reg_str} не существует. Допустимые регистры: R0-R31")
        return reg_num

    def parse_memory_address(self, address_str):
        match = re.match(r'(-?\d+)\((R\d+)\)', address_str)
        if match:
            offset = int(match.group(1))
            base_register = self.parse_register(match.group(2))
            return offset, base_register
        else:
            raise ValueError(f"Некорректная адресация: {address_str}")

    def check_immediate(self, imm, bits=16):
        min_val = -(1 << (bits - 1))  # Минимальное значение для знакового числа
        max_val = (1 << (bits - 1)) - 1  # Максимальное значение для знакового числа
        if not (min_val <= imm <= max_val):
            raise ValueError(f"Непосредственное значение {imm} выходит за пределы {bits}-битного диапазона")
        return imm
