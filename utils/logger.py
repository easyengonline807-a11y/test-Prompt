from datetime import datetime

class Logger:
    """Простой логгер для записи сообщений"""
    
    def __init__(self, log_widget=None):
        self.log_widget = log_widget
    
    def set_widget(self, log_widget):
        """Установить виджет для вывода логов"""
        self.log_widget = log_widget
    
    def log(self, message, level="info"):
        """Вывод сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if self.log_widget:
            self.log_widget.insert("end", full_message, level)
            self.log_widget.see("end")
        else:
            # Если виджет не установлен, выводим в консоль
            print(full_message.strip())
