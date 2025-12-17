import tkinter as tk
from tkinter import scrolledtext

class HotkeyManager:
    """Управление горячими клавишами Ctrl+A/C/V/X"""
    
    def __init__(self, root):
        self.root = root
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """Горячие клавиши (работают на обеих раскладках автоматически)"""
        # Ctrl+A - выделить всё
        self.root.bind_all("<Control-a>", self.select_all)
        self.root.bind_all("<Control-A>", self.select_all)
        
        # Ctrl+C - копировать
        self.root.bind_all("<Control-c>", self.copy_text)
        self.root.bind_all("<Control-C>", self.copy_text)
        
        # Ctrl+V - вставить
        self.root.bind_all("<Control-v>", self.paste_text)
        self.root.bind_all("<Control-V>", self.paste_text)
        
        # Ctrl+X - вырезать
        self.root.bind_all("<Control-x>", self.cut_text)
        self.root.bind_all("<Control-X>", self.cut_text)
    
    def select_all(self, event):
        """Выделить весь текст"""
        widget = self.root.focus_get()
        if isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, tk.END)
        return "break"
    
    def copy_text(self, event):
        """Копировать текст"""
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
        """Вставить текст"""
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
        """Вырезать текст"""
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
