import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import winsound
from pathlib import Path

from gui.settings_tab import SettingsTab
from gui.stats_tab import StatsTab
from gui.log_tab import LogTab

class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, root, config_manager, key_manager, api_client, file_processor, logger):
        self.root = root
        self.config = config_manager
        self.keys = key_manager
        self.api = api_client
        self.processor = file_processor
        self.logger = logger
        
        # Переменные обработки
        self.is_processing = False
        self.is_paused = False
        self.stop_flag = False
        self.processed_files = 0
        self.total_files = 0
        self.start_time = None
        self.processing_times = []
        self.overwrite_all = None
        
        self.setup_window()
        self.create_gui()
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("🤖 Groq Prompt Generator v3.0")
        self.root.resizable(True, True)   # ✅ Можно менять размер
        self.root.minsize(900, 700)       # ✅ Только минимальный размер
        # geometry НЕ УКАЗЫВАЕМ - окно само подстроится!
        self.root.configure(bg="#f0f0f0")
        
        # Светлая тема для ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', background='#e0e0e0', foreground='black', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')])
    
    def create_gui(self):
        """Создание интерфейса"""
        
        import webbrowser
        
        # Информационный блок с активными ссылками
        info_frame = tk.LabelFrame(
            self.root, 
            text="ℹ️ Groq API Instructions", 
            bg="#e8f4f8", 
            fg="#000000", 
            font=("Arial", 9, "bold"), 
            relief=tk.RIDGE, 
            bd=2
        )
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Контейнер для строк
        info_container = tk.Frame(info_frame, bg="#e8f4f8")
        info_container.pack(fill=tk.X, padx=10, pady=5)
        
        # Строка 1 с ссылкой
        line1 = tk.Frame(info_container, bg="#e8f4f8")
        line1.pack(anchor=tk.W, pady=2)
        tk.Label(line1, text="1. Перейдите на ", fg="#000000", bg="#e8f4f8", font=("Arial", 9)).pack(side=tk.LEFT)
        link1 = tk.Label(line1, text="https://console.groq.com", fg="#0066cc", bg="#e8f4f8", font=("Arial", 9, "underline"), cursor="hand2")
        link1.pack(side=tk.LEFT)
        link1.bind("<Button-1>", lambda e: webbrowser.open("https://console.groq.com"))
        
        # Строка 2
        tk.Label(info_container, text="2. Создайте API key в разделе API Keys", fg="#0066cc", bg="#e8f4f8", font=("Arial", 9)).pack(anchor=tk.W, pady=2)
        
        # Строка 3
        tk.Label(info_container, text="3. Лимиты: 30 запросов/мин, 14,400 токенов/день", fg="#008800", bg="#e8f4f8", font=("Arial", 9)).pack(anchor=tk.W, pady=2)
        
        # Строка 4 с ссылкой
        line4 = tk.Frame(info_container, bg="#e8f4f8")
        line4.pack(anchor=tk.W, pady=2)
        tk.Label(line4, text="📧 Временные email: ", fg="#ff6600", bg="#e8f4f8", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        link2 = tk.Label(line4, text="https://emailnator.com", fg="#0066cc", bg="#e8f4f8", font=("Arial", 9, "underline"), cursor="hand2")
        link2.pack(side=tk.LEFT)
        link2.bind("<Button-1>", lambda e: webbrowser.open("https://emailnator.com"))
        
        # Верхняя панель статуса
        top_frame = tk.Frame(self.root, bg="#d0d0d0", height=60, relief=tk.RIDGE, bd=2)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            top_frame,
            text="🟢 Активных: 0 | 🔴 На лимите: 0 | ⏸️ Неактивных: 0",
            font=("Arial", 11, "bold"),
            bg="#d0d0d0",
            fg="#006600"
        )
        self.status_label.pack(pady=5)
        
        self.progress_label = tk.Label(
            top_frame,
            text="Готов к работе",
            font=("Arial", 10),
            bg="#d0d0d0",
            fg="#000000"
        )
        self.progress_label.pack()
        
        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создание вкладок
        tab1 = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab1, text="⚙️ Настройки")
        self.settings_tab = SettingsTab(tab1, self.config)
        
        tab2 = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab2, text="📊 Статистика ключей")
        self.stats_tab = StatsTab(tab2, self.keys)
        
        tab3 = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab3, text="📝 Лог")
        self.log_tab = LogTab(tab3)
        
        # Подключаем виджет лога к логгеру
        self.logger.set_widget(self.log_tab.get_widget())
        
        # Кнопки управления
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Ряд 1: Старт/Пауза/Стоп
        row1 = tk.Frame(button_frame, bg="#f0f0f0")
        row1.pack(fill=tk.X, pady=2)
        
        self.start_button = tk.Button(
            row1, text="▶️ СТАРТ", command=self.start_processing,
            font=("Arial", 12, "bold"), bg="#00cc00", fg="white",
            width=15, height=2, cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            row1, text="⏸️ ПАУЗА", command=self.toggle_pause,
            font=("Arial", 12, "bold"), bg="#ff9900", fg="white",
            width=15, height=2, state=tk.DISABLED, cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            row1, text="⏹️ СТОП", command=self.stop_processing,
            font=("Arial", 12, "bold"), bg="#dd0000", fg="white",
            width=15, height=2, state=tk.DISABLED, cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Ряд 2: Тест API / Сброс статистики / Очистить кэш
        row2 = tk.Frame(button_frame, bg="#f0f0f0")
        row2.pack(fill=tk.X, pady=2)

        tk.Button(
            row2, text="🔍 Тест API", command=self.test_api,
            font=("Arial", 11, "bold"), bg="#0088cc", fg="white",
            width=18, height=1, cursor="hand2", relief=tk.RAISED, bd=3
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            row2, text="🔄 Сброс статистики", command=self.reset_stats,
            font=("Arial", 11, "bold"), bg="#8800cc", fg="white",
            width=18, height=1, cursor="hand2", relief=tk.RAISED, bd=3
        ).pack(side=tk.LEFT, padx=5)

        # ✅ НОВАЯ КНОПКА: Очистить кэш
        tk.Button(
            row2, text="🧹 Очистить кэш", command=self.clean_cache,
            font=("Arial", 11, "bold"), bg="#ff9900", fg="white",
            width=18, height=1, cursor="hand2", relief=tk.RAISED, bd=3
        ).pack(side=tk.LEFT, padx=5)

        
        # Периодическое обновление статистики
        self.root.after(2000, self.periodic_update)
        
        # Автотест первых 3 ключей
        self.root.after(500, self.auto_test_keys)

    def update_status_display(self):
        """Обновление панели статуса"""
        active, on_limit, inactive, nearest_reset = self.keys.get_stats()
        
        reset_text = ""
        if nearest_reset:
            try:
                from datetime import datetime
                delta = nearest_reset - datetime.now()
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                reset_text = f" (восстановление через {hours}ч {minutes}м)"
            except:
                pass
        
        self.status_label.config(
            text=f"🟢 Активных: {active} | 🔴 На лимите: {on_limit}{reset_text} | ⏸️ Неактивных: {inactive}"
        )
        
        # Предупреждение о малом количестве ключей
        if active < 3 and active > 0 and self.is_processing:
            winsound.Beep(1000, 200)
            messagebox.showwarning("⚠️ Внимание", f"Осталось только {active} активных ключей!")
    
    def periodic_update(self):
        """Периодическое обновление интерфейса"""
        if not self.stop_flag:
            self.update_status_display()
            current_model = self.settings_tab.model_var.get()
            self.stats_tab.update_display(model=current_model)
            self.root.after(2000, self.periodic_update)
    
    def test_api(self):
        """Тест первого API ключа"""
        if not self.keys.api_keys:
            messagebox.showerror("Ошибка", "Нет доступных API ключей!")
            return
        
        api_key = self.keys.api_keys[0]
        model = self.settings_tab.model_var.get()
        
        self.logger.log("🔍 Тестирование первого ключа...", "info")
        
        def test_thread():
            result = self.api.test_single_key(api_key)
            
            if result == "ok":
                self.logger.log("✅ Ключ работает!", "success")
                messagebox.showinfo("Успех", "API ключ работает корректно!")
            elif result == "invalid":
                self.logger.log("❌ Ключ невалидный (401)", "error")
                messagebox.showerror("Ошибка", "API ключ невалидный!")
            elif result == "limit":
                self.logger.log("⚠️ Ключ на лимите (429)", "warning")
                messagebox.showwarning("Внимание", "API ключ на лимите!")
            else:
                self.logger.log("⚠️ Ошибка соединения", "warning")
                messagebox.showerror("Ошибка", "Не удалось подключиться к API")
            
            self.update_status_display()
            current_model = self.settings_tab.model_var.get()
            self.stats_tab.update_display(model=current_model)

        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def reset_stats(self):
        """Сброс статистики API ключей"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Сброс статистики")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        
        tk.Label(dialog, text="Выберите что сбросить:", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=20)
        
        def reset_session():
            """Сброс статистики текущей сессии"""
            self.processed_files = 0
            self.total_files = 0
            self.start_time = None
            self.processing_times = []
            self.logger.log("🔄 Статистика сессии сброшена", "info")
            messagebox.showinfo("✅ Успех", "Статистика сессии сброшена!")
            dialog.destroy()
        
        def reset_all():
            """Сброс всей статистики всех API ключей"""
            result = messagebox.askyesno("⚠️ Подтверждение", 
                                         "Сбросить ВСЮ статистику всех API ключей?\n\n"
                                         "Это удалит все данные об использовании ключей.")
            if result:
                self.keys.keys_limits = {}
                self.keys.save_keys_limits()
                self.processed_files = 0
                self.total_files = 0
                self.start_time = None
                self.processing_times = []
                self.stats_tab.update_display()
                self.logger.log("🔄 Вся статистика API ключей сброшена", "info")
                messagebox.showinfo("✅ Успех", "Вся статистика сброшена!")
                dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg="#ffffff")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Сброс сессии", command=reset_session, 
                  width=18, bg="#0088cc", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Сброс всех данных", command=reset_all, 
                  width=18, bg="#cc0000", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    
    def auto_test_keys(self):
        """Автотест первых 3 ключей при запуске"""
        if not self.keys.api_keys:
            return
        
        self.logger.log("🧪 Тестирование первых 3 ключей...", "info")
        
        def test_thread():
            keys_to_test = self.keys.api_keys[:min(3, len(self.keys.api_keys))]
            for i, key in enumerate(keys_to_test, 1):
                result = self.api.test_single_key(key)
                if result == "ok":
                    self.logger.log(f"✅ Ключ {i}/{len(keys_to_test)}: Работает", "success")
                elif result == "invalid":
                    self.logger.log(f"❌ Ключ {i}/{len(keys_to_test)}: Невалидный", "error")
                elif result == "limit":
                    self.logger.log(f"⚠️ Ключ {i}/{len(keys_to_test)}: На лимите", "warning")
                else:
                    self.logger.log(f"⚠️ Ключ {i}/{len(keys_to_test)}: Ошибка", "warning")
                time.sleep(1)
            
            self.logger.log("✅ Тестирование завершено", "success")
            self.update_status_display()
            self.stats_tab.update_display()
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def start_processing(self):
        """Запуск обработки файлов"""
        if self.is_processing:
            return
        
        # Валидация
        chunks_folder = self.settings_tab.chunks_folder_var.get()
        prompts_folder = self.settings_tab.prompts_folder_var.get()
        
        if not chunks_folder:
            messagebox.showerror("❌ Ошибка", "Выберите папку с чанками!")
            return
        
        if not prompts_folder:
            messagebox.showerror("❌ Ошибка", "Выберите папку для промптов!")
            return
        
        if not self.keys.api_keys:
            messagebox.showerror("❌ Ошибка", "Нет доступных API ключей!")
            return
        
        # Получение списка файлов
        files_to_process = self.processor.get_files_to_process(chunks_folder)
        
        if not files_to_process:
            messagebox.showerror("❌ Ошибка", "Папка с чанками пуста!")
            winsound.Beep(800, 300)
            return
        
        # Инициализация
        self.files_to_process = files_to_process
        self.overwrite_all = None
        self.is_processing = True
        self.stop_flag = False
        self.is_paused = False
        self.processed_files = 0
        self.total_files = len(files_to_process)
        self.start_time = time.time()
        self.processing_times = []
        
        # Обновление кнопок
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        
        self.logger.log(f"🚀 Запуск обработки: {self.total_files} файлов", "info")
        
        # Запуск в отдельном потоке
        threading.Thread(target=self.process_files, daemon=True).start()
    
    def toggle_pause(self):
        """Переключение паузы"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_button.config(text="▶️ ПРОДОЛЖИТЬ")
            self.logger.log("⏸️ Пауза", "warning")
        else:
            self.pause_button.config(text="⏸️ ПАУЗА")
            self.logger.log("▶️ Продолжение", "info")
    
    def stop_processing(self):
        """Остановка обработки"""
        self.stop_flag = True
        self.logger.log("⏹️ Остановка...", "warning")
    
    def process_files(self):
        """Обработка всех файлов (выполняется в отдельном потоке)"""
        for file_path in self.files_to_process:
            if self.stop_flag:
                break
            
            # Пауза
            while self.is_paused and not self.stop_flag:
                time.sleep(0.5)
            
            if self.stop_flag:
                break
            
            # Обработка одного файла
            file_start = time.time()
            
            success, status = self.processor.process_file(
                file_path=file_path,
                output_folder=self.settings_tab.prompts_folder_var.get(),
                system_prompt=self.settings_tab.system_prompt_text.get(1.0, tk.END).strip(),
                model=self.settings_tab.model_var.get(),
                temperature=self.settings_tab.temp_var.get(),
                prompts_count=self.settings_tab.prompts_count_var.get(),
                save_raw=self.settings_tab.save_raw_var.get()
            )
            
            if success:
                self.processed_files += 1
                file_time = time.time() - file_start
                self.processing_times.append(file_time)
                
                # Обновление прогресса
                self.update_progress()
                
                # Задержка между файлами (если ключей <= 5)
                if len(self.keys.api_keys) <= 5:
                    delay = self.settings_tab.delay_var.get()
                    if delay > 0:
                        time.sleep(delay)
        
        # Завершение
        self.finish_processing()
    
    def update_progress(self):
        """Обновление прогресс-бара"""
        percent = int((self.processed_files / self.total_files) * 100)
        
        # ETA расчёт
        if len(self.processing_times) > 0:
            avg_time = sum(self.processing_times[-10:]) / len(self.processing_times[-10:])
            remaining = self.total_files - self.processed_files
            eta_seconds = int(avg_time * remaining)
            eta_minutes = eta_seconds // 60
            eta_seconds = eta_seconds % 60
            eta_text = f"ETA: {eta_minutes}м {eta_seconds}с"
        else:
            eta_text = "Расчёт..."
        
        self.progress_label.config(
            text=f"📊 Обработано: {self.processed_files}/{self.total_files} ({percent}%) | {eta_text}"
        )
    
    def finish_processing(self):
        """Завершение обработки"""
        self.is_processing = False
        
        # Обновление кнопок
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸️ ПАУЗА")
        self.stop_button.config(state=tk.DISABLED)
        
        # Статистика
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        if self.stop_flag:
            self.logger.log(f"⏹️ Остановлено: {self.processed_files}/{self.total_files} файлов за {minutes}м {seconds}с", "warning")
            self.progress_label.config(text="⏹️ Остановлено пользователем")
        else:
            self.logger.log(f"🎉 Завершено: {self.processed_files}/{self.total_files} файлов за {minutes}м {seconds}с", "success")
            self.progress_label.config(text="✅ Обработка завершена!")
            winsound.Beep(1000, 500)
    
    def clean_cache(self):
        """🧹 ОТДЕЛЬНАЯ ФУНКЦИЯ: Очистка Python кэша (__pycache__)"""
        result = messagebox.askyesno("🧹 Очистить кэш", 
                                     "Это удалит все скомпилированные Python файлы (.pyc)\n"
                                     "и папки __pycache__.\n\n"
                                     "Приложение будет работать медленнее после первого\n"
                                     "запуска, но будет использовать актуальный код.\n\n"
                                     "Продолжить?")
        if not result:
            return
        
        try:
            from utils.cache_cleaner import CacheCleaner
            cleaner = CacheCleaner(logger=self.logger)
            count = cleaner.clean_all_cache(verbose=True)
            
            self.logger.log(f"✅ Кэш успешно очищен! Удалено элементов: {count}", "success")
            messagebox.showinfo("✅ Успех", 
                               f"Кэш Python успешно очищен!\n\n"
                               f"Удалено элементов: {count}\n\n"
                               f"Примечание: При следующем запуске приложение\n"
                               f"будет работать немного медленнее.")
        except Exception as e:
            self.logger.log(f"❌ Ошибка очистки кэша: {str(e)}", "error")
            messagebox.showerror("❌ Ошибка", 
                                f"Не удалось очистить кэш:\n{str(e)}\n\n"
                                f"Попробуйте очистить вручную через PowerShell:\n"
                                f"Get-ChildItem -Path . -Directory -Filter __pycache__ -Recurse | "
                                f"Remove-Item -Recurse -Force")
