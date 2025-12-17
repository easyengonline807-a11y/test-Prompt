import tkinter as tk
from tkinter import scrolledtext

class LogTab:
    """Вкладка логов"""
    
    def __init__(self, parent):
        self.parent = parent
        self.create_tab()
    
    def create_tab(self):
        """Создание вкладки логов"""
        # Текстовое поле с прокруткой
        self.log_text = scrolledtext.ScrolledText(
            self.parent,
            width=110,
            height=35,
            font=("Consolas", 9),
            bg="#f5f5f5",
            fg="#000000",
            insertbackground="black"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Настройка цветовых тегов
        self.log_text.tag_config("success", foreground="#008800")  # Зелёный
        self.log_text.tag_config("error", foreground="#cc0000")    # Красный
        self.log_text.tag_config("warning", foreground="#ff6600")  # Оранжевый
        self.log_text.tag_config("info", foreground="#0066cc")     # Синий
    
    def get_widget(self):
        """Получить виджет лога для передачи в Logger"""
        return self.log_text
