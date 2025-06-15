# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# --- Пути ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(PROJECT_ROOT, "logos_cache") # Папка для кэша логотипов
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "generated_images")
DATABASE_PATH = os.path.join(PROJECT_ROOT, "cache.db")
FONT_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts", "arial.ttf")

# --- API Ключи (загружаются из .env файла) ---
# Создайте в корне проекта файл .env и запишите в него:
# DEEPL_API_KEY="ваш-ключ"
# APIFOOTBALL_KEY="ваш-ключ"
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY")

# --- Настройки языков ---
SOURCE_LANGUAGE_CODE = "RU"
TARGET_LANGUAGES = ["RU", "FR", "DE", "PL", "PT", "ES", "UK", "EN"]
DEEPL_TARGET_LANG_MAP = {"EN": "EN-US", "PT": "PT-PT"}

# --- Настройки Кэша ---
CACHE_EXPIRATION_DAYS = 30 # Через сколько дней считать логотип устаревшим

# --- Настройки Изображений ---
IMAGE_SIZE = (1280, 1280)
DEFAULT_BACKGROUND_COLOR_1 = (28, 37, 38)
DEFAULT_BACKGROUND_COLOR_2 = (0, 0, 0)
IMAGE_QUALITY = 90 