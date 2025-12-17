import json
from pathlib import Path

class Diagnostic:
    """📊 ДИАГНОСТИКА ПРОБЛЕМ С КОНФИГУРАЦИЕЙ И МОДЕЛЯМИ"""
    
    @staticmethod
    def check_model_sources():
        """🔍 Проверить все источники моделей"""
        print("\n" + "="*70)
        print("📊 ДИАГНОСТИКА ИСТОЧНИКОВ МОДЕЛЕЙ")
        print("="*70)
        
        # 1. Проверить config.json
        print("\n1️⃣ ПРОВЕРКА config.json:")
        print("-" * 70)
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                model = config.get('model')
                models_list = config.get('production_models', [])
                last_check = config.get('last_models_check', 'Не проверялось')
                
                print(f"   ✅ Основная модель: {model}")
                print(f"   ✅ Production модели ({len(models_list)} шт.):")
                for m in models_list:
                    status = "✅" if m == model else "  "
                    print(f"      {status} {m}")
                print(f"   📅 Последняя проверка: {last_check}")
        except Exception as e:
            print(f"   ❌ Ошибка чтения config.json: {e}")
        
        # 2. Проверить размер кэша
        print("\n2️⃣ ПРОВЕРКА РАЗМЕРА __pycache__:")
        print("-" * 70)
        total_size = 0
        count = 0
        for pycache_dir in Path('.').rglob('__pycache__'):
            for file in pycache_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
                    count += 1
        
        size_mb = total_size / (1024 * 1024)
        print(f"   📦 Файлов в кэше: {count}")
        print(f"   📊 Размер: {size_mb:.2f} MB")
        if count > 0:
            print(f"   ⚠️  Рекомендуется очистить кэш!")
        else:
            print(f"   ✅ Кэш чистый")
        
        # 3. Проверить даты модификации ключевых файлов
        print("\n3️⃣ ПРОВЕРКА ДАТ ИЗМЕНЕНИЯ ФАЙЛОВ:")
        print("-" * 70)
        from datetime import datetime
        
        files_to_check = [
            'config.json',
            'main.py',
            'logic/api_client.py',
            'utils/cache_cleaner.py',
            'utils/diagnostic.py'
        ]
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                mtime = Path(file_path).stat().st_mtime
                mod_date = datetime.fromtimestamp(mtime)
                exists = "✅"
            else:
                mod_date = "ОТСУТСТВУЕТ"
                exists = "❌"
            print(f"   {exists} {file_path:30s}: {mod_date}")
        
        # 4. Проверить список папок проекта
        print("\n4️⃣ СТРУКТУРА ПАПОК ПРОЕКТА:")
        print("-" * 70)
        folders = ['config', 'gui', 'logic', 'utils', 'logs']
        for folder in folders:
            if Path(folder).exists():
                files_in_folder = len(list(Path(folder).glob('*.py')))
                print(f"   ✅ {folder:20s}: {files_in_folder} .py файлов")
            else:
                print(f"   ❌ {folder:20s}: ОТСУТСТВУЕТ")
        
        # 5. Проверить наличие requirements
        print("\n5️⃣ ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        print("-" * 70)
        if Path('requirements.txt').exists():
            print(f"   ✅ requirements.txt найден")
        else:
            print(f"   ℹ️  requirements.txt не найден (опционально)")
        
        print("\n" + "="*70)
        print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("="*70 + "\n")
    
    @staticmethod
    def check_deprecated_models():
        """⚠️ Проверить наличие устаревших моделей"""
        print("\n⚠️  ПРОВЕРКА УСТАРЕВШИХ МОДЕЛЕЙ:")
        print("-" * 70)
        
        deprecated = {
            "llama-3.1-70b-versatile": "Заменена на llama-3.3-70b-versatile",
            "gemma2-9b-it": "Вышла из строя 2025-10-08"
        }
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                models = config.get('production_models', [])
                
                found_deprecated = []
                for model in models:
                    if model in deprecated:
                        found_deprecated.append((model, deprecated[model]))
                
                if found_deprecated:
                    print("❌ НАЙДЕНЫ УСТАРЕВШИЕ МОДЕЛИ:")
                    for model, reason in found_deprecated:
                        print(f"   ❌ {model}")
                        print(f"      Причина: {reason}")
                else:
                    print("✅ Устаревшие модели не найдены")
        except Exception as e:
            print(f"❌ Ошибка проверки: {e}")


# Функции для быстрого запуска диагностики
if __name__ == '__main__':
    Diagnostic.check_model_sources()
    Diagnostic.check_deprecated_models()
