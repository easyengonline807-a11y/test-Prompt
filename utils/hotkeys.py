import tkinter as tk
from tkinter import scrolledtext

class HotkeyManager:
    """Управление горячими клавишами Ctrl+A/C/V/X (работает на ВСЕХ раскладках)"""
    
    def __init__(self, root):
        self.root = root
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """Универсальные горячие клавиши через keycode (независимо от раскладки)"""
        
        # Биндим на KeyPress с модификатором Control
        self.root.bind_all("<Control-KeyPress>", self.handle_control_key)
    
    def handle_control_key(self, event):
        """Обработчик Ctrl+клавиша (работает на английской, русской и любой раскладке)"""
        
        # keycode 65 = клавиша A/Ф - Выделить всё
        if event.keycode == 65:
            return self.select_all(event)
        
        # keycode 67 = клавиша C/С - Копировать
        elif event.keycode == 67:
            return self.copy_text(event)
        
        # keycode 86 = клавиша V/М - Вставить
        elif event.keycode == 86:
            return self.paste_text(event)
        
        # keycode 88 = клавиша X/Ч - Вырезать
        elif event.keycode == 88:
            return self.cut_text(event)
    
    def select_all(self, event):
        """Выделить весь текст (Ctrl+A)"""
        widget = self.root.focus_get()
        if isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, tk.END)
        return "break"
    
    def copy_text(self, event):
        """Копировать текст (Ctrl+C)"""
        widget = self.root.focus_get()
        try:
            if isinstance(widget, tk.Entry):
                text = widget.selection_get()
            elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
                text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except:
            pass
        return "break"
    
    def paste_text(self, event):
        """Вставить текст (Ctrl+V)"""
        widget = self.root.focus_get()
        try:
            text = self.root.clipboard_get()
            if isinstance(widget, tk.Entry):
                widget.insert(tk.INSERT, text)
            elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
                widget.insert(tk.INSERT, text)
        except:
            pass
        return "break"
    
    def cut_text(self, event):
        """Вырезать текст (Ctrl+X)"""
        widget = self.root.focus_get()
        try:
            if isinstance(widget, tk.Entry):
                text = widget.selection_get()
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
                text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except:
            pass
        return "break"
