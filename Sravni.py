import tkinter as tk
from tkinter import messagebox

class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=25, bg="#F0F0F0", highlightthickness=0, **kwargs)
        self.text_widget = text_widget
        
    def redraw(self):
        self.delete("all")
        last_line = self.text_widget.index("end-1c").split(".")[0]
        new_width = max(25, (len(last_line) * 9) + 5)
        self.config(width=new_width)

        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(new_width - 5, y, anchor="ne", text=linenum, fill="#888888", font=("Segoe UI", 9))
            i = self.text_widget.index("%s+1line" % i)

def copy_for_sql():
    data = entry_main.get("1.0", tk.END).strip().split('\n')
    filtered_data = [line.strip() for line in data if line.strip()]
    if not filtered_data:
        messagebox.showwarning("Внимание", "Окно 1 пустое!")
        return
    sql_string = ",\n".join([f"'{item}'" for item in filtered_data])
    root.clipboard_clear()
    root.clipboard_append(sql_string)
    messagebox.showinfo("Успех", "Формат SQL скопирован!")

def copy_results():
    data = entry_result.get("1.0", tk.END).strip()
    if not data:
        messagebox.showwarning("Внимание", "Окно потерь пустое!")
        return
    root.clipboard_clear()
    root.clipboard_append(data)
    messagebox.showinfo("Успех", "Потери скопированы!")

def find_losses():
    table1 = [line.strip() for line in entry_main.get("1.0", tk.END).split('\n') if line.strip()]
    table2 = set(line.strip().lower() for line in entry_secondary.get("1.0", tk.END).split('\n') if line.strip())
    
    losses = []
    seen = set()
    for item in table1:
        item_lower = item.lower()
        if item_lower not in table2 and item_lower not in seen:
            losses.append(item)
            seen.add(item_lower)

    entry_result.config(state=tk.NORMAL)
    entry_result.delete("1.0", tk.END)
    entry_result.insert(tk.END, "\n".join(losses))
    entry_result.config(state=tk.DISABLED)
    update_counters()

def clear_all():
    entry_main.delete("1.0", tk.END)
    entry_secondary.delete("1.0", tk.END)
    entry_result.config(state=tk.NORMAL)
    entry_result.delete("1.0", tk.END)
    entry_result.config(state=tk.DISABLED)
    update_counters()

def update_counters(event=None):
    c1 = len([l for l in entry_main.get("1.0", "end-1c").split('\n') if l.strip()])
    c2 = len([l for l in entry_secondary.get("1.0", "end-1c").split('\n') if l.strip()])
    c3 = len([l for l in entry_result.get("1.0", "end-1c").split('\n') if l.strip()])
    label_main.config(text=f"Окно 1 [{c1}]:")
    label_secondary.config(text=f"Окно 2 [{c2}]:")
    label_res_count.config(text=f"Потери [{c3}]:")
    line_nums_main.redraw()
    line_nums_sec.redraw()
    line_nums_res.redraw()

def create_custom_text(parent, height=10, is_input=True):
    container = tk.Frame(parent, bg="white", highlightbackground="#CCCCCC", highlightthickness=1)
    container.pack(fill="both", expand=True)
    txt = tk.Text(container, height=height, undo=True, font=("Segoe UI", 10), relief="flat", padx=5, pady=5, wrap="none")
    ln = LineNumbers(container, txt)
    ln.pack(side="left", fill="y")
    scroll_y = tk.Scrollbar(container, orient="vertical", command=lambda *args: (txt.yview(*args), ln.redraw()))
    scroll_y.pack(side="right", fill="y")
    txt.config(yscrollcommand=scroll_y.set)
    txt.pack(side="left", fill="both", expand=True)
    txt.bind("<MouseWheel>", lambda e: root.after(1, ln.redraw))
    txt.bind("<Button-1>", lambda e: root.after(1, ln.redraw))
    if is_input: txt.bind("<KeyRelease>", update_counters)
    return txt, ln

root = tk.Tk()
root.title("Sravni v5.4")
root.geometry("1100x800")
root.configure(bg="#F0F2F5")

# Горячие клавиши
root.bind_class("Text", "<<Paste>>", lambda e: root.after(1, update_counters))
root.bind_class("Text", "<Control-v>", lambda e: e.widget.event_generate("<<Paste>>"))
root.bind_class("Text", "<Control-V>", lambda e: e.widget.event_generate("<<Paste>>"))
root.bind_class("Text", "<Control-c>", lambda e: e.widget.event_generate("<<Copy>>"))
root.bind_class("Text", "<Control-C>", lambda e: e.widget.event_generate("<<Copy>>"))
root.bind_class("Text", "<Control-a>", lambda e: e.widget.event_generate("<<SelectAll>>"))

top_frame = tk.Frame(root, bg="#F0F2F5")
top_frame.pack(fill="both", expand=True, padx=15, pady=15)
f1 = tk.Frame(top_frame, bg="#F0F2F5")
f1.pack(side="left", fill="both", expand=True, padx=(0, 10))
label_main = tk.Label(f1, text="Окно 1:", bg="#F0F2F5", font=("Segoe UI", 10, "bold"))
label_main.pack(anchor="w")
entry_main, line_nums_main = create_custom_text(f1)

f2 = tk.Frame(top_frame, bg="#F0F2F5")
f2.pack(side="right", fill="both", expand=True, padx=(10, 0))
label_secondary = tk.Label(f2, text="Окно 2:", bg="#F0F2F5", font=("Segoe UI", 10, "bold"))
label_secondary.pack(anchor="w")
entry_secondary, line_nums_sec = create_custom_text(f2)

btn_frame = tk.Frame(root, bg="#F0F2F5")
btn_frame.pack(pady=10)

# ПОРЯДОК КНОПОК ИЗМЕНЕН
tk.Button(btn_frame, text="Найти потери", command=find_losses, bg="#0078D7", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=8).pack(side="left", padx=5)
tk.Button(btn_frame, text="Скопировать потери", command=copy_results, bg="#0078D7", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=8).pack(side="left", padx=5)
tk.Button(btn_frame, text="Скопировать в SQL", command=copy_for_sql, bg="#28A745", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=8).pack(side="left", padx=5)
tk.Button(btn_frame, text="Очистить всё", command=clear_all, bg="#E1E1E1", font=("Segoe UI", 10), padx=15, pady=8).pack(side="left", padx=5)

res_frame = tk.Frame(root, bg="#F0F2F5")
res_frame.pack(fill="both", expand=True, padx=15, pady=15)
label_res_count = tk.Label(res_frame, text="Потери:", bg="#F0F2F5", font=("Segoe UI", 10, "bold"))
label_res_count.pack(anchor="w")
entry_result, line_nums_res = create_custom_text(res_frame, height=8, is_input=False)
entry_result.config(state=tk.DISABLED, bg="#FFFFFF")

root.mainloop()
