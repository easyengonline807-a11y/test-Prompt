import os
from pathlib import Path
from datetime import datetime

class FileProcessor:
    """Обработка файлов с чанками и промптами"""
    
    def __init__(self, api_client, logger=None):
        self.api_client = api_client
        self.logger = logger
    
    def log(self, message, level="info"):
        """Вывод в лог"""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(message)
    
    def read_chunk(self, file_path):
        """Чтение текста из чанка"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            self.log(f"❌ Ошибка чтения {file_path.name}: {str(e)}", "error")
            return None
    
    def parse_prompts(self, response_text):
        """Парсинг промптов из ответа API"""
        prompts = []
        
        for line in response_text.split('\n'):
            line = line.strip()
            
            # Фильтр: минимум 20 символов
            if len(line) > 20:
                # Удаляем нумерацию в начале (1., 2), №1, etc)
                if line[0].isdigit():
                    # Ищем точку или скобку после цифры
                    for i, char in enumerate(line):
                        if char in '.):':
                            line = line[i+1:].strip()
                            break
                
                if line:
                    prompts.append(line)
        
        return prompts
    
    def save_prompts(self, prompts, output_path):
        """Сохранение промптов в файл"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for prompt in prompts:
                    f.write(prompt + '\n')
            return True
        except Exception as e:
            self.log(f"❌ Ошибка сохранения: {str(e)}", "error")
            return False
    
    def save_raw_response(self, response_text, filename):
        """Сохранение сырого ответа API для отладки"""
        try:
            os.makedirs("logs/raw_responses", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_path = f"logs/raw_responses/{timestamp}_{filename}.txt"
            
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            return True
        except:
            return False

    def process_file(self, file_path, output_folder, system_prompt, model, temperature, prompts_count, save_raw=False):
        """Обработка одного файла с чанком"""
        
        # Чтение чанка
        chunk_text = self.read_chunk(file_path)
        if not chunk_text:
            return False, "read_error"
        
        # Подстановка {n} в system prompt
        system_prompt_formatted = system_prompt.replace("{n}", str(prompts_count))
        
        # Отправка запроса к API
        self.log(f"🔄 Обработка: {file_path.name}", "info")
        response, status = self.api_client.send_request(
            user_message=chunk_text,
            system_prompt=system_prompt_formatted,
            model=model,
            temperature=temperature
        )
        
        if status != "success" or not response:
            # ✅ НОВОЕ: Регистрируем ошибку
            if hasattr(self.api_client, 'key_manager') and self.api_client.key_manager:
                # Получаем текущий использованный ключ
                current_key_index = self.api_client.key_manager.current_key_index - 1
                if current_key_index < 0:
                    current_key_index = len(self.api_client.key_manager.api_keys) - 1
                
                if current_key_index < len(self.api_client.key_manager.api_keys):
                    api_key = self.api_client.key_manager.api_keys[current_key_index]
                    self.api_client.key_manager.add_error(api_key)
            
            return False, status
        
        # Сохранение сырого ответа (если включено)
        if save_raw:
            self.save_raw_response(response, file_path.stem)
        
        # Парсинг промптов
        prompts = self.parse_prompts(response)
        
        if not prompts:
            self.log(f"⚠️ Не удалось распарсить промпты из {file_path.name}", "warning")
            
            # ✅ НОВОЕ: Регистрируем ошибку парсинга
            if hasattr(self.api_client, 'key_manager') and self.api_client.key_manager:
                current_key_index = self.api_client.key_manager.current_key_index - 1
                if current_key_index < 0:
                    current_key_index = len(self.api_client.key_manager.api_keys) - 1
                
                if current_key_index < len(self.api_client.key_manager.api_keys):
                    api_key = self.api_client.key_manager.api_keys[current_key_index]
                    self.api_client.key_manager.add_error(api_key)
            
            return False, "parse_error"
        
        # Сохранение промптов
        output_path = Path(output_folder) / file_path.name
        success = self.save_prompts(prompts, output_path)
        
        if success:
            # ✅ НОВОЕ: Регистрируем успешную обработку
            if hasattr(self.api_client, 'key_manager') and self.api_client.key_manager:
                current_key_index = self.api_client.key_manager.current_key_index - 1
                if current_key_index < 0:
                    current_key_index = len(self.api_client.key_manager.api_keys) - 1
                
                if current_key_index < len(self.api_client.key_manager.api_keys):
                    api_key = self.api_client.key_manager.api_keys[current_key_index]
                    self.api_client.key_manager.add_file_processed(api_key)
                    self.api_client.key_manager.add_prompts_generated(api_key, len(prompts))
            
            self.log(f"✅ Сохранено {len(prompts)} промптов → {output_path.name}", "success")
            return True, "success"
        else:
            # ✅ НОВОЕ: Регистрируем ошибку сохранения
            if hasattr(self.api_client, 'key_manager') and self.api_client.key_manager:
                current_key_index = self.api_client.key_manager.current_key_index - 1
                if current_key_index < 0:
                    current_key_index = len(self.api_client.key_manager.api_keys) - 1
                
                if current_key_index < len(self.api_client.key_manager.api_keys):
                    api_key = self.api_client.key_manager.api_keys[current_key_index]
                    self.api_client.key_manager.add_error(api_key)
            
            return False, "save_error"

    def get_files_to_process(self, chunks_folder):
        """Получить список .txt файлов для обработки"""
        chunks_path = Path(chunks_folder)
        
        if not chunks_path.exists():
            return []
        
        return list(chunks_path.glob("*.txt"))
    
    def check_file_exists(self, file_path, output_folder, overwrite_all):
        """Проверка существования выходного файла"""
        output_path = Path(output_folder) / file_path.name
        
        if not output_path.exists():
            return True, overwrite_all  # Файл не существует - можно обрабатывать
        
        # Файл существует
        if overwrite_all is not None:
            # Уже есть решение "применить ко всем"
            return overwrite_all, overwrite_all
        
        # Нужно спросить пользователя (это сделает GUI)
        return None, None
