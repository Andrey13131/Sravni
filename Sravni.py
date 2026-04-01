import tkinter as tk

def get_clean_lines(text_widget):
    raw_text = text_widget.get("1.0", tk.END)
    lines = raw_text.splitlines()
    return [item.strip() for item in lines if item.strip()]

def update_input_counters():
    """Мгновенно обновляет счётчики строк при любом изменении текста."""
    m_len = len(get_clean_lines(entry_main))
    s_len = len(get_clean_lines(entry_secondary))
    label_main.config(text=f"Основная таблица (Окно 1) [{m_len} строк]:")
    label_secondary.config(text=f"Вторая таблица (Окно 2) [{s_len} строк]:")

def find_losses():
    main_data = get_clean_lines(entry_main)
    secondary_data = get_clean_lines(entry_secondary)
    
    # Игнорирование регистра
    secondary_set_lower = set(item.lower() for item in secondary_data)
    
    # Сравниваем, сохраняя оригинальное написание
    losses = [item for item in main_data if item.lower() not in secondary_set_lower]
    
    result_text.delete("1.0", tk.END)
    
    if losses:
        for loss in losses:
            result_text.insert(tk.END, f"{loss}\n")
        label_result.config(text=f"Результат (недостающие строки) [{len(losses)} строк]:")
    else:
        result_text.insert(tk.END, "Потерь не найдено.\n")
        label_result.config(text="Результат (недостающие строки) [0 строк]:")

def copy_for_sql():
    """Форматирует данные из Окна 1 для SQL: 'data1',\n'data2' и копирует в буфер."""
    data = get_clean_lines(entry_main)
    if data:
        # Форматируем: каждая строка в одинарных кавычках, разделены запятой и новой строкой
        sql_formatted = ",\n".join([f"'{item}'" for item in data])
        
        root.clipboard_clear()
        root.clipboard_append(sql_formatted)
        
        # Уведомление в окне результата
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"--- SQL ФОРМАТ ---\nСкопировано строк: {len(data)}\n\nТеперь просто вставьте (Ctrl+V) в SQL скрипт.")
        label_result.config(text=f"Результат (SQL COPY) [{len(data)} строк]")
    else:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Окно 1 пустое. Нечего копировать для SQL.")

def clear_all():
    entry_main.delete("1.0", tk.END)
    entry_secondary.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    update_input_counters()
    label_result.config(text="Результат (недостающие строки) [0 строк]:")

def copy_result():
    losses_text = result_text.get("1.0", tk.END).strip()
    if losses_text and "SQL ФОРМАТ" not in losses_text:
        root.clipboard_clear()
        root.clipboard_append(losses_text)

# --- НАСТРОЙКА ГЛАВНОГО ОКНА ---
root = tk.Tk()
root.title("Sravni v5.0 | SQL & Analysis Tool")
root.geometry("1100x750")
root.configure(bg="#F0F2F5")

# Обработчик горячих клавиш (защита от багов раскладки)
def handle_ctrl_keys(event):
    if event.keycode == 67: # C
        event.widget.event_generate("<<Copy>>")
        return "break"
    elif event.keycode == 86: # V
        event.widget.event_generate("<<Paste>>")
        root.after(10, update_input_counters)
        return "break"
    elif event.keycode == 88: # X
        event.widget.event_generate("<<Cut>>")
        root.after(10, update_input_counters)
        return "break"
    elif event.keycode == 65: # A
        event.widget.tag_add("sel", "1.0", "end")
        return "break"
    elif event.keycode == 90: # Z
        try: 
            event.widget.event_generate("<<Undo>>")
            root.after(10, update_input_counters)
        except tk.TclError: pass
        return "break"

root.bind_class("Text", "<Control-KeyPress>", handle_ctrl_keys, "+")

# Шрифты
font_title = ("Segoe UI", 10, "bold")
font_text = ("Consolas", 10) 
font_btn_bold = ("Segoe UI", 10, "bold")
font_btn_normal = ("Segoe UI", 10)

def create_text_with_scrollbar(parent, height=10, is_input=True):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)
    scrollbar = tk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    text_widget = tk.Text(frame, height=height, yscrollcommand=scrollbar.set, 
                          undo=True, font=font_text, relief="flat", padx=10, pady=10)
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)
    if is_input:
        text_widget.bind("<KeyRelease>", lambda e: root.after(10, update_input_counters))
    return text_widget

# --- ИНТЕРФЕЙС ---
top_frame = tk.Frame(root, bg="#F0F2F5")
top_frame.pack(fill="both", expand=True, padx=15, pady=(15, 5))

# Окно 1
left_frame = tk.Frame(top_frame, bg="#F0F2F5")
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
label_main = tk.Label(left_frame, text="Основная таблица (Окно 1) [0 строк]:", bg="#F0F2F5", font=font_title)
label_main.pack(anchor="w", pady=(0, 5))
entry_main = create_text_with_scrollbar(left_frame, is_input=True)

# Окно 2
right_frame = tk.Frame(top_frame, bg="#F0F2F5")
right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
label_secondary = tk.Label(right_frame, text="Вторая таблица (Окно 2) [0 строк]:", bg="#F0F2F5", font=font_title)
label_secondary.pack(anchor="w", pady=(0, 5))
entry_secondary = create_text_with_scrollbar(right_frame, is_input=True)

# Кнопки
button_frame = tk.Frame(root, bg="#F0F2F5")
button_frame.pack(pady=15)

tk.Button(button_frame, text="Найти потери", command=find_losses, 
          bg="#0078D7", fg="white", font=font_btn_bold, 
          relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=10)

# НОВАЯ КНОПКА SQL
tk.Button(button_frame, text="Скопировать в SQL", command=copy_for_sql, 
          bg="#28A745", fg="white", font=font_btn_bold, 
          relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=10)

tk.Button(button_frame, text="Очистить всё", command=clear_all, 
          bg="#E1E1E1", fg="#333333", font=font_btn_normal, 
          relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=10)

tk.Button(button_frame, text="Скопировать результат", command=copy_result, 
          bg="#E1E1E1", fg="#333333", font=font_btn_normal, 
          relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=10)

# Результат
bottom_frame = tk.Frame(root, bg="#F0F2F5")
bottom_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
label_result = tk.Label(bottom_frame, text="Результат (недостающие строки) [0 строк]:", bg="#F0F2F5", font=font_title)
label_result.pack(anchor="w", pady=(0, 5))
result_text = create_text_with_scrollbar(bottom_frame, height=8, is_input=False)

root.mainloop()
