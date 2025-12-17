import requests
import json
from datetime import datetime

class ModelValidator:
    """✅ НОВОЕ: Валидация и обновление списка доступных моделей Groq API"""
    
    PRODUCTION_MODELS = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "meta-llama/llama-guard-4-12b"
    ]
    
    DEPRECATED_MODELS = [
        "llama-3.1-70b-versatile",  # Заменена на llama-3.3-70b-versatile
        "gemma2-9b-it"  # Вышла из строя 2025-10-08
    ]
    
    def __init__(self, logger=None):
        self.logger = logger
        self.api_url = "https://api.groq.com/openai/v1/models"
    
    def log(self, message, level="info"):
        """Вывод в лог"""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(message)
    
    def get_available_models(self, api_key):
        """📡 Получить актуальный список моделей из Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(self.api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = [model['id'] for model in data.get('data', [])]
                self.log(f"✅ Получен список моделей: {len(models)} моделей", "success")
                return models
            else:
                self.log(f"❌ Ошибка API при получении моделей (код {response.status_code})", "error")
                return None
        except Exception as e:
            self.log(f"⚠️ Не удалось подключиться к Groq API: {str(e)}", "warning")
            return None
    
    def filter_production_models(self, available_models):
        """🔍 Отфильтровать только Production модели"""
        production = []
        
        for model in available_models:
            if model in self.PRODUCTION_MODELS:
                production.append(model)
        
        return production
    
    def check_deprecated_models(self, available_models):
        """⚠️ Найти устаревшие модели"""
        deprecated = []
        
        for model in available_models:
            if model in self.DEPRECATED_MODELS:
                deprecated.append(model)
        
        if deprecated:
            self.log(f"⚠️ Найдены устаревшие модели: {deprecated}", "warning")
        
        return deprecated
    
    def validate_config_models(self, config_file):
        """🔐 Проверить, что в config.json используются только Production модели"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model = config.get('model')
            production_models = config.get('production_models', self.PRODUCTION_MODELS)
            
            # Проверяем основную модель
            if model not in production_models:
                self.log(f"❌ Основная модель '{model}' не в Production списке!", "error")
                self.log(f"   Рекомендуемые модели: {', '.join(production_models)}", "info")
                return False
            
            self.log(f"✅ Config валиден! Используется Production модель: {model}", "success")
            return True
        
        except Exception as e:
            self.log(f"❌ Ошибка проверки config: {str(e)}", "error")
            return False
    
    def update_config(self, config_file, api_key):
        """🔄 ЕЖЕНЕДЕЛЬНОЕ ОБНОВЛЕНИЕ: Обновить Production модели в config.json"""
        try:
            # Получаем актуальный список
            available_models = self.get_available_models(api_key)
            
            if available_models is None:
                self.log("⚠️ Не удалось получить список моделей для обновления", "warning")
                return False
            
            # Фильтруем Production модели
            production = self.filter_production_models(available_models)
            
            if not production:
                self.log("❌ No Production models found!", "error")
                production = self.PRODUCTION_MODELS
            
            # Читаем config
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Обновляем
            config['production_models'] = production
            config['last_models_check'] = datetime.now().strftime("%Y-%m-%d")
            
            # Сохраняем
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            self.log(f"✅ Config обновлен! Production модели: {', '.join(production)}", "success")
            return True
        
        except Exception as e:
            self.log(f"❌
