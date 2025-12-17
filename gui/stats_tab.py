# gui/stats_tab.py - ПОЛНОСТЬЮ ПЕРЕПИСАТЬ

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class StatsTab:
    """Вкладка статистики ключей"""
    
    def __init__(self, parent, key_manager):
        self.parent = parent
        self.key_manager = key_manager
        self.create_tab()
    
    def create_tab(self):
        """Создание вкладки статистики"""
        container = tk.Frame(self.parent, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(
            container,
            text="📊 Статистика использования ключей",
            bg="#ffffff",
            fg="black",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # ✅ ПАМЯТКА: Лимиты моделей В СТОЛБИК
        info_frame = tk.Frame(container, bg="#f0f8ff", relief=tk.RIDGE, borderwidth=2)
        info_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            info_frame,
            text="📋 Лимиты моделей (RPD - запросов в день):",
            bg="#f0f8ff",
            fg="#000000",
            font=("Segoe UI", 10, "bold") 
        ).pack(anchor="w", padx=10, pady=5)

        from logic.model_limits import MODEL_LIMITS

        info_text = ""
        for model_name, model_data in MODEL_LIMITS.items():
            emoji = model_data['name'].split()[0]
            rpd = model_data['rpd']
            info_text += f"{emoji} {model_name}: {rpd:,} RPD\n"

        tk.Label(
            info_frame,
            text=info_text.strip(),
            bg="#f0f8ff",
            fg="#333333",
            font=("Arial", 9),
            justify="left"
        ).pack(anchor="w", padx=20, pady=5)


        # Настройка стиля таблицы
        style = ttk.Style()
        style.configure("Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            borderwidth=1
        )
        style.configure("Treeview.Heading",
            background="#e0e0e0",
            foreground="black",
            borderwidth=1
        )
        style.map('Treeview', background=[('selected', '#cce5ff')])
        
        # ✅ НОВАЯ КОЛОНКА: "RPD Лимит"
        columns = ("Ключ", "Запросы", "Токены IN", "Токены OUT", "Промпты", "Файлы", "Ошибки", "Статус", "RPD Лимит")
        self.stats_tree = ttk.Treeview(container, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            if col == "Ключ":
                self.stats_tree.column(col, width=100)
            elif col == "Статус":
                self.stats_tree.column(col, width=110)
            elif col == "RPD Лимит":  # ✅ НОВАЯ колонка - шире
                self.stats_tree.column(col, width=160)
            else:
                self.stats_tree.column(col, width=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscroll=scrollbar.set)
        
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_display(self, model=None):  # ← ДОБАВЛЯЕМ ПАРАМЕТР model
        """✅ ИСПРАВЛЕННЫЙ: Обновление отображения таблицы с RPD"""
        try:
            from logic.model_limits import MODEL_LIMITS
        except ImportError:
            MODEL_LIMITS = {"llama-3.3-70b-versatile": {"rpd": 1_000}}
        
        # Очистка таблицы
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        # ✅ ИСПРАВЛЕНО: Получаем ПЕРЕДАННУЮ модель (или берем из config.json)
        if model is None:
            try:
                import json
                with open('config.json', 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    model = config_data.get('model', 'llama-3.3-70b-versatile')
            except:
                model = 'llama-3.3-70b-versatile'
        
        # ✅ Теперь берем правильный лимит для ТЕКУЩЕЙ модели
        rpd_limit = MODEL_LIMITS.get(model, {}).get('rpd', 1000)
        
        # Заполнение таблицы (остальной код без изменений)
        for key in self.key_manager.api_keys:
            key_id = key[-8:]
            
            if key_id in self.key_manager.keys_limits:
                data = self.key_manager.keys_limits[key_id]
                
                # Определение статуса
                if data.get('permanently_invalid', False):
                    status = "❌ Невалидный"
                elif data.get('tokens_used_today', 0) >= 14400:
                    status = "🔴 TPD лимит"
                elif data.get('requests_this_minute', 0) >= 30:
                    status = "🟡 RPM лимит"
                else:
                    status = "🟢 Активен"
                
                # Расчёт RPD статуса с цветовым индикатором
                total_requests = data.get('total_requests', 0)
                rpd_percentage = (total_requests / rpd_limit * 100) if rpd_limit > 0 else 0
                
                # Цветовой индикатор на основе процента
                if rpd_percentage < 50:
                    rpd_indicator = f"🟢 {total_requests}/{rpd_limit} ({rpd_percentage:.0f}%)"
                elif rpd_percentage < 80:
                    rpd_indicator = f"🟡 {total_requests}/{rpd_limit} ({rpd_percentage:.0f}%)"
                else:
                    rpd_indicator = f"🔴 {total_requests}/{rpd_limit} ({rpd_percentage:.0f}%)"
                
                # Вставка в таблицу
                self.stats_tree.insert('', tk.END, values=(
                    f"...{key_id}",
                    data.get('total_requests', 0),
                    data.get('total_tokens_in', 0),
                    data.get('total_tokens_out', 0),
                    data.get('prompts_generated', 0),
                    data.get('files_processed', 0),
                    data.get('errors', 0),
                    status,
                    rpd_indicator
                ))
            else:
                # Ключ ещё не использовался
                rpd_indicator = f"🟢 0/{rpd_limit} (0%)"
                
                self.stats_tree.insert('', tk.END, values=(
                    f"...{key_id}",
                    0, 0, 0, 0, 0, 0,
                    "🟢 Активен",
                    rpd_indicator
                ))
