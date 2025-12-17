import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import json
from pathlib import Path

class SettingsTab:
    """Вкладка настроек"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        self.create_tab()
    
    def load_models_from_config(self):
        """📌 НОВОЕ: Загрузить список моделей из config.json"""
        try:
            # Пытаемся загрузить из config.json
            if hasattr(self.config, 'production_models'):
                return self.config.production_models
            
            # Fallback: загружаем напрямую из файла
            with open('config.json', 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                models = config_data.get('production_models', [])
                if models:
                    return models
        except:
            pass
        
        # Последний fallback - Production модели
        return [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "meta-llama/llama-guard-4-12b"
        ]
    
    def create_tab(self):
        """Создание вкладки настроек"""
        container = tk.Frame(self.parent, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        row = 0
        
        # Модель
        tk.Label(container, text="🤖 Модель:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.model_var = tk.StringVar(value=self.config.get("model", "llama-3.3-70b-versatile"))
        model_combo = ttk.Combobox(container, textvariable=self.model_var, width=40, state="readonly")
        
        # ✅ ИСПРАВЛЕНО: Загружаем модели из config.json вместо hardcode
        available_models = self.load_models_from_config()
        model_combo['values'] = available_models
        
        model_combo.grid(row=row, column=1, sticky=tk.W, pady=10)
        model_combo.bind("<<ComboboxSelected>>", lambda e: self.on_setting_change())
        row += 1
        
        # Температура
        tk.Label(container, text="🌡️ Температура:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.temp_var = tk.DoubleVar(value=self.config.get("temperature", 0.7))
        temp_frame = tk.Frame(container, bg="#ffffff")
        temp_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        tk.Scale(
            temp_frame, 
            from_=0.0, 
            to=2.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.temp_var, 
            length=300,
            bg="#ffffff",
            fg="black",
            troughcolor="#e0e0e0",
            highlightthickness=0,
            command=lambda e: self.on_setting_change()
        ).pack(side=tk.LEFT)
        
        temp_label = tk.Label(temp_frame, width=5, bg="#ffffff", fg="black")
        temp_label.pack(side=tk.LEFT, padx=5)
        
        def update_temp_label(*args):
            temp_label.config(text=f"{self.temp_var.get():.2f}")
        self.temp_var.trace_add('write', update_temp_label)
        update_temp_label()
        row += 1
        
        # Количество промптов
        tk.Label(container, text="📊 Количество промптов:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.prompts_count_var = tk.IntVar(value=self.config.get("prompts_count", 5))
        ttk.Spinbox(container, from_=1, to=10, textvariable=self.prompts_count_var, width=10, command=self.on_setting_change).grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1
        
        # Задержка
        tk.Label(container, text="⏱️ Задержка между файлами:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        delay_frame = tk.Frame(container, bg="#ffffff")
        delay_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.delay_var = tk.IntVar(value=self.config.get("delay", 1))
        ttk.Spinbox(delay_frame, from_=0, to=60, textvariable=self.delay_var, width=10, command=self.on_setting_change).pack(side=tk.LEFT)
        tk.Label(delay_frame, text=" сек", bg="#ffffff", fg="black").pack(side=tk.LEFT)
        tk.Label(delay_frame, text="(Авто 0 если ключей > 5)", bg="#ffffff", fg="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Сохранять сырые ответы
        self.save_raw_var = tk.BooleanVar(value=self.config.get("save_raw_responses", False))
        tk.Checkbutton(
            container,
            text="☑️ Сохранять сырые ответы API (для отладки)",
            variable=self.save_raw_var,
            bg="#ffffff",
            fg="black",
            selectcolor="#e0e0e0",
            font=("Arial", 10),
            command=self.on_setting_change
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Папка с чанками
        tk.Label(container, text="📁 Папка с чанками:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        chunks_frame = tk.Frame(container, bg="#ffffff")
        chunks_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.chunks_folder_var = tk.StringVar(value=self.config.get("chunks_folder", ""))
        tk.Entry(chunks_frame, textvariable=self.chunks_folder_var, width=35, bg="white", fg="black", insertbackground="black").pack(side=tk.LEFT)
        tk.Button(chunks_frame, text="📂", command=lambda: self.select_folder("chunks_folder"), width=3, bg="#e0e0e0", fg="black", cursor="hand2").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Папка с промптами
        tk.Label(container, text="💾 Папка с промптами:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        prompts_frame = tk.Frame(container, bg="#ffffff")
        prompts_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.prompts_folder_var = tk.StringVar(value=self.config.get("prompts_folder", ""))
        tk.Entry(prompts_frame, textvariable=self.prompts_folder_var, width=35, bg="white", fg="black", insertbackground="black").pack(side=tk.LEFT)
        tk.Button(prompts_frame, text="📂", command=lambda: self.select_folder("prompts_folder"), width=3, bg="#e0e0e0", fg="black", cursor="hand2").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # System prompt
        tk.Label(container, text="📝 System Prompt:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.NW, pady=10)
        self.system_prompt_text = scrolledtext.ScrolledText(
            container, 
            width=50, 
            height=8, 
            font=("Consolas", 9),
            bg="white",
            fg="black",
            insertbackground="black",
            wrap=tk.WORD
        )
        self.system_prompt_text.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        default_prompt = self.config.get("system_prompt", 
            "Ты создаешь промпты для генерации исторических изображений. "
            "На основе предоставленного текста о военной истории создай {n} детальных описаний "
            "ключевых сцен для генератора изображений. "
            "Каждый промпт должен быть на русском языке, содержать описание сцены, персонажей, "
            "техники, окружения и атмосферы. Промпты должны быть визуально яркими и детальными. "
            "Каждый промпт пиши с новой строки без нумерации и лишних символов.")
        
        self.system_prompt_text.insert(1.0, default_prompt)
        self.system_prompt_text.bind("<KeyRelease>", lambda e: self.on_setting_change())
    
    def select_folder(self, field_name):
        """Выбор папки"""
        folder = filedialog.askdirectory()
        if folder:
            if field_name == "chunks_folder":
                self.chunks_folder_var.set(folder)
            elif field_name == "prompts_folder":
                self.prompts_folder_var.set(folder)
            self.on_setting_change()
    
    def on_setting_change(self):
        """Автосохранение при изменении настроек"""
        self.config.config["model"] = self.model_var.get()
        self.config.config["temperature"] = self.temp_var.get()
        self.config.config["chunks_folder"] = self.chunks_folder_var.get()
        self.config.config["prompts_folder"] = self.prompts_folder_var.get()
        self.config.config["system_prompt"] = self.system_prompt_text.get(1.0, tk.END).strip()
        self.config.config["prompts_count"] = self.prompts_count_var.get()
        self.config.config["delay"] = self.delay_var.get()
        self.config.config["save_raw_responses"] = self.save_raw_var.get()
        self.config.save_config()
