# logic/model_limits.py

MODEL_LIMITS = {
    "llama-3.1-8b-instant": {
        "name": "🚀 БЫСТРАЯ МОДЕЛЬ",
        "rpd": 14400,
        "tpd": 500000,
        "rpm": 30,
        "tpm": 6000
    },
    "llama-3.3-70b-versatile": {
        "name": "🧠 УНИВЕРСАЛЬНАЯ МОДЕЛЬ",
        "rpd": 1000,
        "tpd": 100000,
        "rpm": 30,
        "tpm": 12000
    },
    "openai/gpt-oss-120b": {
        "name": "⚡ МОЩНАЯ МОДЕЛЬ",
        "rpd": 1000,
        "tpd": 200000,
        "rpm": 30,
        "tpm": 8000
    },
    "openai/gpt-oss-20b": {
        "name": "⚙️ СРЕДНЯЯ МОДЕЛЬ",
        "rpd": 1000,
        "tpd": 200000,
        "rpm": 30,
        "tpm": 8000
    },
    "meta-llama/llama-guard-4-12b": {
        "name": "🚀 МОДЕРАЦИЯ",
        "rpd": 14400,
        "tpd": 500000,
        "rpm": 30,
        "tpm": 15000
    }
}

def get_model_rpd(model_name):
    """Получить RPD лимит для модели"""
    return MODEL_LIMITS.get(model_name, {}).get('rpd', 1000)

def get_model_info(model_name):
    """Получить всю информацию о модели"""
    return MODEL_LIMITS.get(model_name, {})
