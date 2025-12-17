"""
Groq Prompt Generator v3.0
Главный файл запуска приложения
"""
import tkinter as tk
import os
import sys
from pathlib import Path

# ✅ ОТКЛЮЧИТЬ СОЗДАНИЕ .pyc ФАЙЛОВ ПРИ РАЗРАБОТКЕ
sys.dont_write_bytecode = True

# Импорт компонента для очистки кэша
from utils.cache_cleaner import cleanup_on_startup, CacheCleaner

# Импорт всех компонентов
from config.settings import ConfigManager
from logic.key_manager import KeyManager
from logic.api_client import GroqAPIClient
from logic.file_processor import FileProcessor
from gui.main_window import MainWindow
from utils.hotkeys import HotkeyManager
from utils.lock_file import LockFileManager
from utils.logger import Logger


def main():
    """Точка входа в приложение"""
    
    # ✅ НОВОЕ: Очистка кэша при запуске в режиме разработки
    DEV_MODE = True  # Установите False для продакшена
    if DEV_MODE:
        print("🧹 Режим разработки - очистка кэша Python...")
        cleanup_on_startup(dev_mode=True)
    
    # Создание главного окна
    root = tk.Tk()
    
    # 1. Проверка lock-файла (защита от двойного запуска)
    lock_manager = LockFileManager()
    if not lock_manager.check_lock_file():
        return
    
    # 2. Загрузка конфигурации
    config = ConfigManager()
    
    # 3. Инициализация менеджера ключей
    keys = KeyManager()
    
    # 4. Создание логгера
    logger = Logger()
    
    # 5. Создание API клиента
    api_client = GroqAPIClient(keys, logger)
    
    # 6. Создание обработчика файлов
    file_processor = FileProcessor(api_client, logger)
    
    # 7. Создание главного окна
    app = MainWindow(root, config, keys, api_client, file_processor, logger)
    
    # 8. Настройка горячих клавиш
    HotkeyManager(root)
    
    # 9. Обработка закрытия окна
    def on_closing():
        lock_manager.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 10. Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()
