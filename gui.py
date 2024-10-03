import tkinter as tk
from tkinter import filedialog, messagebox
from processor import EmulatorMIPS
from disassembler import DisassemblerMIPS
from exceptions import EmptyException


class AssemblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Emulator")

        # Frame для кнопок сверху
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=20)

        # Кнопки для запуска, загрузки и сохранения программы
        self.run_button = tk.Button(button_frame, text="Запустить", command=self.run)
        self.run_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(button_frame, text="Следующий шаг", command=self.next_step)
        self.next_button.pack(side=tk.LEFT)
        self.load_button = tk.Button(button_frame, text="Загрузить из файла", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(button_frame, text="Сохранить в файл", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT)
        # self.prev_button = tk.Button(button_frame, text="<", command=self.previous_step)
        # self.prev_button.pack(side=tk.LEFT)


        # Используем Frame для текстовой области и дополнительных элементов
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Поле для ввода ассемблерного кода
        self.text_area = tk.Text(content_frame, height=20, width=60)
        self.text_area.grid(row=0, column=0, padx=10, pady=10)

        # Область для отображения регистров
        self.reg_frame = tk.LabelFrame(content_frame, text="Регистры")
        self.reg_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')

        # Область для отображения памяти
        self.mem_frame = tk.LabelFrame(content_frame, text="Память")
        self.mem_frame.grid(row=0, column=2, padx=10, pady=10, sticky='n')

        self.processor = EmulatorMIPS()
        self.disassembler = DisassemblerMIPS()
        self.processor.data_memory[0:3] = [1, 2, 3, 4]

        self.reg_labels = []
        for i in range(10):  # Отображаем первые 10 регистров
            label = tk.Label(self.reg_frame, text=f"R{i}: 0")
            label.pack(anchor='w')
            self.reg_labels.append(label)

        self.mem_labels = []
        for i in range(10):  # Отображаем первые 10 ячеек памяти
            label = tk.Label(self.mem_frame, text=f"Mem[{i * 4}]: 0")
            label.pack(anchor='w')
            self.mem_labels.append(label)

        self.update_register_display()
        self.update_memory_display()
        self.run_flag = 0

    # Функция для обновления отображения регистров
    def update_register_display(self):
        for i in range(10):
            value = self.processor.registers[i]
            self.reg_labels[i].config(text=f"R{i}: {value}")

    # Функция для обновления отображения памяти
    def update_memory_display(self):
        for i in range(10):
            value = self.processor.data_memory[i]
            self.mem_labels[i].config(text=f"Mem[{i * 4}]: {value}")

    # Запуск программы на эмуляторе
    def run(self):
        code = self.text_area.get("1.0", tk.END).strip()
        if code:
            try:
                program = self.disassembler.disassemble(code)

                self.processor.load_program(program)

                self.processor.run()
                self.run_flag = 1
                self.highlight_line(self.processor.pc)
                print("Программа успешно запущена")

                self.update_register_display()
                self.update_memory_display()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showwarning("Внимание", "Поле ввода команд пустое!")

    def next_step(self):
        if self.run_flag == 1:
            try:
                self.processor.run()
                self.update_register_display()
                self.update_memory_display()
                self.highlight_line(self.processor.pc)
            except EmptyException as e:
                messagebox.showinfo("Внимание", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showerror("Ошибка", "Программа не запущена")

    # Загрузка программы из файла
    def load_from_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    code = file.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert(tk.END, code)
                print(f"Программа загружена из {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    # Сохранение программы в файл
    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                code = self.text_area.get("1.0", tk.END)
                with open(file_path, "w") as file:
                    file.write(code)
                print(f"Программа сохранена в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {str(e)}")

    def highlight_line(self, line):
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        self.text_area.tag_add("highlight", f"{line}.0", f"{line}.end")
        self.text_area.tag_configure("highlight", background="yellow")


if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblerGUI(root)
    root.mainloop()
