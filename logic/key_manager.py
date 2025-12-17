import json
import os
import threading
import re
from datetime import datetime, timedelta
from tkinter import messagebox

class KeyManager:
    """Управление API ключами (загрузка, ротация, лимиты)"""
    
    def __init__(self, keys_file="API_keys.txt", limits_file="logs/keys_limits.json"):
        self.keys_file = keys_file
        self.limits_file = limits_file
        self.api_keys = []
        self.keys_limits = {}
        self.current_key_index = 0
        self.request_counter = 0
        self.file_lock = threading.Lock()
        
        # Создаём папку для логов
        os.makedirs("logs", exist_ok=True)
        
        # Загружаем данные
        self.load_api_keys()
        self.load_keys_limits()
    
    def load_api_keys(self):
        """Загрузка API ключей из файла"""
        self.api_keys = []
        if os.path.exists(self.keys_file):
            with open(self.keys_file, 'r', encoding='utf-8') as f:
                for line in f:
                    key = line.strip()
                    if key and not key.startswith('#'):
                        self.api_keys.append(key)
        
        if not self.api_keys:
            messagebox.showerror(
                "❌ Ошибка",
                f"Файл {self.keys_file} пуст или не найден!\n\n"
                "Добавьте API ключи (один на строку)"
            )
    
    def reload_api_keys(self):
        """Перезагрузка API ключей"""
        old_count = len(self.api_keys)
        self.load_api_keys()
        new_count = len(self.api_keys)
        return old_count, new_count
    
    def load_keys_limits(self):
        """Загрузка лимитов ключей из файла"""
        if os.path.exists(self.limits_file):
            with self.file_lock:
                with open(self.limits_file, 'r', encoding='utf-8') as f:
                    self.keys_limits = json.load(f)
        else:
            self.keys_limits = {}
        
        self.reset_expired_limits()
    
    def save_keys_limits(self):
        """Сохранение лимитов ключей"""
        with self.file_lock:
            with open(self.limits_file, 'w', encoding='utf-8') as f:
                json.dump(self.keys_limits, f, indent=2)
    
    def reset_expired_limits(self):
        """Сброс устаревших лимитов"""
        now = datetime.now()
        changed = False
        
        for key_id, data in self.keys_limits.items():
            # Daily reset
            if 'daily_reset_at' in data:
                try:
                    if data['daily_reset_at'] and isinstance(data['daily_reset_at'], str):
                        reset_time = datetime.fromisoformat(data['daily_reset_at'])
                        if now > reset_time:
                            data['tokens_used_today'] = 0
                            data['daily_reset_at'] = (now + timedelta(days=1)).isoformat()
                            changed = True
                except (ValueError, TypeError):
                    data['daily_reset_at'] = (now + timedelta(days=1)).isoformat()
                    changed = True
            
            # RPM reset
            if 'rpm_reset_at' in data:
                try:
                    if data['rpm_reset_at'] and isinstance(data['rpm_reset_at'], str):
                        reset_time = datetime.fromisoformat(data['rpm_reset_at'])
                        if now > reset_time:
                            data['requests_this_minute'] = 0
                            data['rpm_reset_at'] = None
                            changed = True
                except (ValueError, TypeError):
                    data['rpm_reset_at'] = None
                    changed = True
        
        if changed:
            self.save_keys_limits()
    
    def get_next_key(self):
        """Round-robin выбор следующего валидного ключа"""
        if not self.api_keys:
            return None
        
        # Перечитываем ключи раз в 5 запросов
        self.request_counter += 1
        if self.request_counter % 5 == 0:
            self.reload_api_keys()
        
        attempts = 0
        max_attempts = len(self.api_keys)
        
        while attempts < max_attempts:
            key = self.api_keys[self.current_key_index]
            key_id = key[-8:]
            
            # Переход к следующему
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            attempts += 1
            
            # Проверка валидности
            if key_id in self.keys_limits:
                limits = self.keys_limits[key_id]
                
                if limits.get('permanently_invalid', False):
                    continue
                
                # Проверка RPM
                if limits.get('requests_this_minute', 0) >= 30:
                    if limits.get('rpm_reset_at'):
                        try:
                            if isinstance(limits['rpm_reset_at'], str):
                                reset_time = datetime.fromisoformat(limits['rpm_reset_at'])
                                if datetime.now() < reset_time:
                                    continue
                        except:
                            pass
                
                # Проверка TPD
                if limits.get('tokens_used_today', 0) >= 14400:
                    continue
            
            return key
        
        return None
        
    def update_key_limits(self, api_key, headers):
        """✅ ИСПРАВЛЕННЫЙ: Обновление лимитов из заголовков API"""
        key_id = api_key[-8:]
        
        if key_id not in self.keys_limits:
            self.keys_limits[key_id] = {
                "total_requests": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "prompts_generated": 0,
                "files_processed": 0,
                "errors": 0,
                "requests_this_minute": 0,
                "tokens_used_today": 0,
                "rpm_reset_at": None,
                "daily_reset_at": (datetime.now() + timedelta(days=1)).isoformat(),
                "invalid_attempts": 0,
                "permanently_invalid": False
            }
        
        # ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Увеличиваем счётчик запросов!
        self.keys_limits[key_id]['total_requests'] = self.keys_limits[key_id].get('total_requests', 0) + 1
        
        # Сброс invalid_attempts при успешном запросе
        self.keys_limits[key_id]['invalid_attempts'] = 0
        
        # Обновление из заголовков
        if 'x-ratelimit-remaining-tokens' in headers:
            remaining_tokens = int(headers['x-ratelimit-remaining-tokens'])
            limit_tokens = int(headers.get('x-ratelimit-limit-tokens', 14400))
            self.keys_limits[key_id]['tokens_used_today'] = limit_tokens - remaining_tokens
        
        if 'x-ratelimit-remaining-requests' in headers:
            remaining_requests = int(headers['x-ratelimit-remaining-requests'])
            limit_requests = int(headers.get('x-ratelimit-limit-requests', 30))
            self.keys_limits[key_id]['requests_this_minute'] = limit_requests - remaining_requests
        
        if 'x-ratelimit-reset-requests' in headers:
            reset_str = headers['x-ratelimit-reset-requests']
            reset_seconds = self.parse_reset_time(reset_str)
            self.keys_limits[key_id]['rpm_reset_at'] = (datetime.now() + timedelta(seconds=reset_seconds)).isoformat()
        
        self.save_keys_limits()

    def parse_reset_time(self, reset_str):
        """Парсинг времени сброса из строки типа '1m30s'"""
        total_seconds = 0
        
        hours = re.search(r'(\d+)h', reset_str)
        minutes = re.search(r'(\d+)m', reset_str)
        seconds = re.search(r'([\d.]+)s', reset_str)
        
        if hours:
            total_seconds += int(hours.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += float(seconds.group(1))
        
        return int(total_seconds)
    
    def mark_key_invalid(self, api_key):
        """Отметка ключа как невалидного"""
        key_id = api_key[-8:]
        
        if key_id not in self.keys_limits:
            self.keys_limits[key_id] = {
                "total_requests": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "prompts_generated": 0,
                "files_processed": 0,
                "errors": 0,
                "invalid_attempts": 1,
                "permanently_invalid": False
            }
        else:
            self.keys_limits[key_id]['invalid_attempts'] = self.keys_limits[key_id].get('invalid_attempts', 0) + 1
        
        # После 3 попыток - permanent invalid
        if self.keys_limits[key_id]['invalid_attempts'] >= 3:
            self.keys_limits[key_id]['permanently_invalid'] = True
        
        self.save_keys_limits()
    
    def get_stats(self):
        """Получить статистику по всем ключам"""
        active = 0
        on_limit = 0
        inactive = 0
        nearest_reset = None
        
        for key in self.api_keys:
            key_id = key[-8:]
            
            if key_id in self.keys_limits:
                data = self.keys_limits[key_id]
                
                if data.get('permanently_invalid', False):
                    inactive += 1
                elif data.get('tokens_used_today', 0) >= 14400:
                    on_limit += 1
                    if data.get('daily_reset_at'):
                        try:
                            reset_time = datetime.fromisoformat(data['daily_reset_at'])
                            if nearest_reset is None or reset_time < nearest_reset:
                                nearest_reset = reset_time
                        except:
                            pass
                elif data.get('requests_this_minute', 0) >= 30:
                    on_limit += 1
                    if data.get('rpm_reset_at'):
                        try:
                            reset_time = datetime.fromisoformat(data['rpm_reset_at'])
                            if nearest_reset is None or reset_time < nearest_reset:
                                nearest_reset = reset_time
                        except:
                            pass
                else:
                    active += 1
            else:
                active += 1
        
        return active, on_limit, inactive, nearest_reset
    
    # ✅ НОВЫЕ МЕТОДЫ ДЛЯ ОБНОВЛЕНИЯ СЧЁТЧИКОВ СТАТИСТИКИ
    
    def add_prompts_generated(self, api_key, count):
        """Добавить количество сгенерированных промптов"""
        key_id = api_key[-8:]
        if key_id in self.keys_limits:
            self.keys_limits[key_id]['prompts_generated'] = \
                self.keys_limits[key_id].get('prompts_generated', 0) + count
            self.save_keys_limits()

    def add_file_processed(self, api_key):
        """Зафиксировать обработку одного файла"""
        key_id = api_key[-8:]
        if key_id in self.keys_limits:
            self.keys_limits[key_id]['files_processed'] = \
                self.keys_limits[key_id].get('files_processed', 0) + 1
            self.save_keys_limits()

    def add_error(self, api_key):
        """Зафиксировать ошибку при обработке"""
        key_id = api_key[-8:]
        if key_id in self.keys_limits:
            self.keys_limits[key_id]['errors'] = \
                self.keys_limits[key_id].get('errors', 0) + 1
            self.save_keys_limits()

