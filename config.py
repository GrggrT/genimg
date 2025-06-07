# config.py
# Файл для хранения всех настроек и констант проекта.

# --- Пути к ресурсам ---
# Укажите абсолютные пути для надежности
LOGO_DIR = r"C:\1\logos"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"

# --- Настройки API ---
DEEPL_API_KEY = "8f34b9b3-a664-42ad-8e3c-c1a4e9ec748d:fx"

# --- Настройки языков ---
SOURCE_LANGUAGE_CODE = "RU"
TARGET_LANGUAGES = ["RU", "FR", "DE", "PL", "PT", "ES", "UK", "EN"]
DEEPL_TARGET_LANG_MAP = {
    "EN": "EN-US", "PT": "PT-PT", "FR": "FR", "DE": "DE", 
    "PL": "PL", "ES": "ES", "UK": "UK", "RU": "RU"
}

# --- Настройки GUI и ограничений ---
MAX_MATCHES_IN_LIST = 10  # Макс. постов (одиночных или экспрессов) в списке на генерацию
MAX_LEGS_IN_EXPRESS = 10  # Макс. событий в одном экспрессе

# --- Настройки изображений ---
IMAGE_SIZE = (1280, 1280)
DEFAULT_BACKGROUND_COLOR_1 = (28, 37, 38) # Начальный цвет градиента
DEFAULT_BACKGROUND_COLOR_2 = (0, 0, 0)   # Конечный цвет градиента
IMAGE_QUALITY = 90