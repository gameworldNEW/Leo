import re
import os
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import subprocess

# Попытка импорта clr для C# (если нет - будет ошибка только при вызове drop)
try:
    import clr
except ImportError:
    clr = None

# --- ЯДРО LEO ---
class LeoInterpreter:
    def __init__(self, output_func):
        self.vars = {}
        self.external_modules = {}
        self.pc = 0
        self.lines = []
        self.output = output_func

    def run(self, code):
        self.vars = {}
        self.pc = 0
        code = re.sub(r'\|.*?\|', '', code, flags=re.DOTALL)
        raw_lines = code.split('\n')
        self.lines = [l.split('[]')[0].strip() for l in raw_lines if l.split('[]')[0].strip()]
        
        while self.pc < len(self.lines):
            line = self.lines[self.pc]
            if not self.execute(line): break
            self.pc += 1

    def prepare_expr(self, expr):
        expr = expr.replace(',', '.').replace('@', '**').replace('CMP', '==')
        expr = re.sub(r'\btrue\b', 'True', expr)
        expr = re.sub(r'\bfalse\b', 'False', expr)
        return expr

    def execute(self, line):
        try:
            if line.startswith('drop '):
                if not clr: 
                    self.output("[Error] Установите pythonnet (pip install pythonnet)\n")
                    return True
                match = re.search(r'drop "(.*?)" ([\w\.]+)', line)
                if match:
                    path, full_class = match.groups()
                    clr.AddReference(os.path.abspath(path))
                    parts = full_class.split('.')
                    namespace, class_name = ".".join(parts[:-1]), parts[-1]
                    exec(f"from {namespace} import {class_name}", {}, self.external_modules)
                    self.output(f"[System] Модуль {class_name} подключен\n")
                return True

            if '=' in line and '(' in line:
                for cls_name, cls_obj in self.external_modules.items():
                    if f"{cls_name}." in line:
                        clean = re.sub(r'^(float|int|str|bool)\s+', '', line)
                        var_n, call = clean.split('=', 1)
                        self.vars[var_n.strip()] = eval(call.strip(), {cls_name: cls_obj}, self.vars)
                        return True

            if line.startswith('if '):
                m = re.match(r'if\s+(.*)\s+right\s+(.*)', line)
                if m and eval(self.prepare_expr(m.group(1)), {}, self.vars):
                    self.execute(m.group(2))
                return True

            if line.startswith('DLYA '):
                m = re.match(r'DLYA\s+(\w+)\s+(.*)', line)
                if m:
                    count = int(self.vars.get(m.group(1), m.group(1)))
                    for _ in range(count): self.execute(m.group(2))
                return True

            if line.startswith('type="'):
                res = re.search(r'type="(.*)"', line)
                if res: self.output(res.group(1) + "\n")
            elif line.startswith('typeval='):
                var_name = line.split('=')[1].strip()
                self.output(str(self.vars.get(var_name, "Null")) + "\n")
            elif 'input("' in line:
                m = re.search(r'(\w+)\s*=\s*input\("(.*)"\)', line)
                if m: self.vars[m.group(1)] = simpledialog.askstring("Leo", m.group(2))
            elif '=' in line:
                clean = re.sub(r'^(float|int|str|bool)\s+', '', line)
                n, e = clean.split('=', 1)
                self.vars[n.strip()] = eval(self.prepare_expr(e.strip()), {}, self.vars)
            elif line == "END": return False
        except Exception as e:
            self.output(f"[Error] {e} в строке: {line}\n")
        return True

# --- ИНТЕРФЕЙС ---
class LeoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Leo Language IDE v3.5")
        self.root.geometry("950x700")

        # Кнопки
        btns = tk.Frame(root)
        btns.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btns, text="▶ ЗАПУСК", command=self.run_code, bg="#28a745", fg="white", width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btns, text="🔨 СБОРКА C#", command=self.build_cs, bg="#007bff", fg="white").pack(side=tk.LEFT, padx=2)

        # Контейнер для строк и кода
        main_editor = tk.Frame(root)
        main_editor.pack(expand=True, fill=tk.BOTH, padx=10)

        self.line_nums = tk.Text(main_editor, width=4, padx=5, font=("Consolas", 12), bg="#2d2d2d", fg="#858585", state="disabled")
        self.line_nums.pack(side=tk.LEFT, fill=tk.Y)

        self.txt = scrolledtext.ScrolledText(main_editor, font=("Consolas", 12), bg="#252526", fg="#d4d4d4", insertbackground="white")
        self.txt.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.console = scrolledtext.ScrolledText(root, height=10, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 11))
        self.console.pack(fill=tk.X, padx=10, pady=5)

        # Бинды
        self.txt.bind("<KeyRelease>", self.on_change)
        self.txt.vbar.config(command=self.sync_scroll)
        self.line_nums.bind("<MouseWheel>", lambda e: "break") # Отключаем скролл номеров отдельно

        self.txt.insert("1.0", 'type="Hello!"\nint x = 5\ntypeval=x\nEND')
        self.on_change()

    def sync_scroll(self, *args):
        self.txt.yview(*args)
        self.line_nums.yview(*args)

    def on_change(self, event=None):
        self.update_line_numbers()
        self.update_colors()

    def update_line_numbers(self):
        self.line_nums.config(state="normal")
        self.line_nums.delete('1.0', tk.END)
        lines = self.txt.get('1.0', tk.END).count('\n')
        self.line_nums.insert('1.0', "\n".join(str(i) for i in range(1, lines + 1)))
        self.line_nums.yview_moveto(self.txt.yview()[0])
        self.line_nums.config(state="disabled")

    def update_colors(self):
        t = self.txt
        for tag in t.tag_names(): t.tag_delete(tag)
        rules = [
            ("#C586C0", r'\b(if|right|DLYA|END|drop)\b'),
            ("#569CD6", r'\b(int|float|str|bool)\b'),
            ("#CE9178", r'".*?"'),
            ("#6A9955", r'\[.*\]'),
            ("#DCDCAA", r'\b(type|typeval|input)\b')
        ]
        for color, reg in rules:
            t.tag_configure(color, foreground=color)
            for m in re.finditer(reg, t.get("1.0", tk.END)):
                t.tag_add(color, f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    def run_code(self):
        self.console.delete(1.0, tk.END)
        LeoInterpreter(lambda t: self.console.insert(tk.END, t)).run(self.txt.get("1.0", tk.END))

    def build_cs(self):
        csc = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
        if not os.path.exists("lib.cs"): 
            messagebox.showerror("!", "Файл lib.cs не найден!"); return
        res = subprocess.run([csc, "/target:library", "/out:MyLib.dll", "lib.cs"], capture_output=True, text=True)
        messagebox.showinfo("C# Build", "Успешно!" if res.returncode==0 else res.stderr)

if __name__ == "__main__":
    root = tk.Tk()
    LeoEditor(root)
    root.mainloop()
