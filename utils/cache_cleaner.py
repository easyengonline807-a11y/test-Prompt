import os
import shutil
from pathlib import Path

class CacheCleaner:
    """🗑️ ОЧИСТКА PYTHON КЭША И УСТАРЕВШИХ ФАЙЛОВ"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.project_root = Path(__file__).parent.parent
    
    def log(self, message, level="info"):
        """Вывод в лог"""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(message)
    
    def clean_pycache(self, verbose=True):
        """🗑️ Удалить все __pycache__ папки в проекте"""
        deleted_count = 0
        
        # Рекурсивно ищем все __pycache__ директории
        for pycache_dir in self.project_root.rglob('__pycache__'):
            try:
                shutil.rmtree(pycache_dir)
                if verbose:
                    self.log(f"✅ Удалена папка: {pycache_dir}", "info")
                deleted_count += 1
            except Exception as e:
                self.log(f"❌ Ошибка удаления {pycache_dir}: {str(e)}", "error")
        
        if deleted_count > 0:
            self.log(f"✅ Очищено {deleted_count} __pycache__ папок", "success")
        else:
            self.log("ℹ️ Нет __pycache__ папок для удаления", "info")
        
        return deleted_count
    
    def clean_pyc_files(self, verbose=True):
        """🗑️ Удалить все .pyc файлы в проекте"""
        deleted_count = 0
        
        for pyc_file in self.project_root.rglob('*.pyc'):
            try:
                pyc_file.unlink()
                if verbose:
                    self.log(f"✅ Удален файл: {pyc_file}", "info")
                deleted_count += 1
            except Exception as e:
                self.log(f"❌ Ошибка удаления {pyc_file}: {str(e)}", "error")
        
        if deleted_count > 0:
            self.log(f"✅ Удалено {deleted_count} .pyc файлов", "success")
        
        return deleted_count
    
    def clean_all_cache(self, verbose=True):
        """🗑️ ПОЛНАЯ ОЧИСТКА: __pycache__ + .pyc файлы"""
        self.log("🧹 ЗАПУСК ПОЛНОЙ ОЧИСТКИ КЭША...", "info")
        
        pycache_count = self.clean_pycache(verbose=False)
        pyc_count = self.clean_pyc_files(verbose=False)
        
        total = pycache_count + pyc_count
        if total > 0:
            self.log(f"🧹 Кэш очищен! Удалено элементов: {total}", "success")
        else:
            self.log("ℹ️ Кэш уже чистый", "info")
        
        return total
    
    @staticmethod
    def get_pycache_size():
        """📊 Получить размер всех __pycache__ папок"""
        total_size = 0
        count = 0
        
        for pycache_dir in Path('.').rglob('__pycache__'):
            for file in pycache_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
                    count += 1
        
        size_mb = total_size / (1024 * 1024)
        return count, size_mb


def cleanup_on_startup(logger=None, dev_mode=False):
    """🧹 Очистить кэш при запуске в режиме разработки"""
    if dev_mode or os.getenv('DEV_MODE', 'false').lower() == 'true':
        cleaner = CacheCleaner(logger=logger)
        cleaner.clean_all_cache(verbose=True)
