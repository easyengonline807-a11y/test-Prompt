import requests
import time
import winsound
from datetime import datetime

class GroqAPIClient:
    """Клиент для работы с Groq API"""
    
    def __init__(self, key_manager, logger=None):
        self.key_manager = key_manager
        self.logger = logger
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def log(self, message, level="info"):
        """Вывод в лог"""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(message)
    
    def send_request(self, user_message, system_prompt, model, temperature, max_retries=3):
        """Отправка запроса к Groq API с повторами при ошибках"""
        
        for attempt in range(max_retries):
            # Получаем следующий доступный ключ
            api_key = self.key_manager.get_next_key()
            
            if not api_key:
                self.log("❌ Нет доступных API ключей!", "error")
                winsound.Beep(800, 500)
                return None, "no_keys"
            
            key_id = api_key[-8:]
            
            try:
                self.log(f"📤 Запрос с ключом ...{key_id} (попытка {attempt + 1}/{max_retries})", "info")
                
                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": temperature
                    },
                    timeout=30
                )
                
                # Обработка ответа
                if response.status_code == 200:
                    # Успех
                    self.key_manager.update_key_limits(api_key, response.headers)
                    data = response.json()
                    answer = data['choices'][0]['message']['content']
                    self.log(f"✅ Успех с ключом ...{key_id}", "success")
                    return answer, "success"
                
                elif response.status_code == 401:
                    # Невалидный ключ
                    self.log(f"❌ Ключ ...{key_id} невалидный (401)", "error")
                    self.key_manager.mark_key_invalid(api_key)
                    continue  # Пробуем следующий ключ
                
                elif response.status_code == 429:
                    # Rate limit - прогрессивная задержка
                    self.key_manager.update_key_limits(api_key, response.headers)
                    
                    delays = [5, 10, 15]
                    if attempt < len(delays):
                        delay = delays[attempt]
                        self.log(f"⚠️ Rate limit (429), ожидание {delay} сек...", "warning")
                        time.sleep(delay)
                        continue
                    else:
                        self.log(f"⚠️ Rate limit (429), переключение ключа", "warning")
                        continue
                
                elif response.status_code == 500:
                    # Ошибка сервера - сразу следующий ключ
                    self.log(f"⚠️ Ошибка сервера (500), переключение ключа", "warning")
                    continue
                
                else:
                    # Другая ошибка
                    self.log(f"❌ Ошибка {response.status_code}: {response.text[:100]}", "error")
                    time.sleep(5)
                    continue
            
            except requests.exceptions.Timeout:
                self.log(f"⚠️ Timeout с ключом ...{key_id}", "warning")
                time.sleep(5)
                continue
            
            except requests.exceptions.ConnectionError:
                self.log(f"⚠️ Ошибка соединения, повтор через 5 сек...", "warning")
                time.sleep(5)
                continue
            
            except Exception as e:
                self.log(f"❌ Исключение: {str(e)}", "error")
                time.sleep(5)
                continue
        
        # Все попытки исчерпаны
        self.log(f"❌ Не удалось выполнить запрос после {max_retries} попыток", "error")
        return None, "failed"
    
    def test_single_key(self, api_key):
        """Тест одного ключа"""
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                },
                timeout=15
            )
            
            if response.status_code == 200:
                self.key_manager.update_key_limits(api_key, response.headers)
                return "ok"
            elif response.status_code == 401:
                self.key_manager.mark_key_invalid(api_key)
                return "invalid"
            elif response.status_code == 429:
                self.key_manager.update_key_limits(api_key, response.headers)
                return "limit"
            else:
                return "error"
        except:
            return "error"
