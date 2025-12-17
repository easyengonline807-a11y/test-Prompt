import os
from tkinter import messagebox

class LockFileManager:
    """Управление lock-файлом для предотвращения двойного запуска"""
    
    def __init__(self, lock_file=".running"):
        self.lock_file = lock_file
    
    def check_lock_file(self):
        """Проверка существования lock файла"""
        if os.path.exists(self.lock_file):
            result = messagebox.askyesno(
                "⚠️ Программа уже запущена",
                "Обнаружен файл блокировки. Другой экземпляр программы может быть запущен.\n\n"
                "Продолжить запуск? (Это может привести к конфликтам данных)"
            )
            if not result:
                return False
            else:
                os.remove(self.lock_file)
        
        # Создание lock файла
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        return True
    
    def cleanup(self):
        """Удаление lock файла при закрытии"""
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
