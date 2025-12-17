import json
import os

class ConfigManager:
    """Управление настройками программы (config.json)"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации из файла"""
        default_config = {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "chunks_folder": "",
            "prompts_folder": "",
            "system_prompt": "",
            "prompts_count": 5,
            "delay": 1,
            "save_raw_responses": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Объединяем с default (на случай новых полей)
                    default_config.update(loaded_config)
                    return default_config
            except:
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Сохранение конфигурации в файл"""
        if config:
            self.config = config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """Получить значение настройки"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Установить значение настройки"""
        self.config[key] = value
        self.save_config()
