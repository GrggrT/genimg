# downloader.py (ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ РЕПОЗИТОРИЯ Leo4815162342)
import os
import requests
import re
from tqdm import tqdm

# --- Настройки ---
# URL на README.md с логотипами в формате RAW
README_URL = 'https://raw.githubusercontent.com/Leo4815162342/football-logos/main/README.md'
# Базовый URL для скачивания сырых файлов логотипов
BASE_LOGO_URL = 'https://raw.githubusercontent.com/Leo4815162342/football-logos/main'

# Папка, куда будут сохраняться логотипы. Убедитесь, что она совпадает с LOGO_DIR в вашем config.py
LOCAL_LOGO_DIR = r'C:\1\logos'

# --- Основная логика скрипта ---
def download_logos():
    """
    Скачивает все логотипы, перечисленные в README.md, в локальную папку.
    """
    # 1. Создаем папку, если ее нет
    if not os.path.exists(LOCAL_LOGO_DIR):
        print(f"Создание папки для логотипов: {LOCAL_LOGO_DIR}")
        os.makedirs(LOCAL_LOGO_DIR)

    # 2. Получаем содержимое README.md
    print(f"Получение списка логотипов из: {README_URL}")
    try:
        response = requests.get(README_URL)
        response.raise_for_status() # Проверка на ошибки HTTP (включая 404)
        readme_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"!!! Ошибка при получении README.md: {e}")
        print("!!! Проверьте ваше интернет-соединение или правильность ссылки README_URL.")
        return

    # 3. Находим все относительные пути к файлам логотипов в README
    # Ищем шаблоны вида: /logos/country/128x128/team-name.png
    logo_paths = re.findall(r'(/logos/[^)]+\.png)', readme_content)
    unique_logo_paths = sorted(list(set(logo_paths))) # Убираем дубликаты
    
    if not unique_logo_paths:
        print("!!! Не удалось найти пути к логотипам в README файле. Возможно, изменилась структура репозитория.")
        return

    print(f"Найдено {len(unique_logo_paths)} уникальных логотипов для скачивания.")
    
    # 4. Скачиваем каждый логотип
    success_count = 0
    fail_count = 0
    
    for relative_path in tqdm(unique_logo_paths, desc="Скачивание логотипов"):
        # Формируем полный URL для скачивания
        file_url = f"{BASE_LOGO_URL}{relative_path}"
        
        # Получаем имя файла из пути
        filename = os.path.basename(relative_path)
        
        local_filepath = os.path.join(LOCAL_LOGO_DIR, filename)
        
        if os.path.exists(local_filepath):
            continue

        try:
            logo_response = requests.get(file_url, stream=True)
            logo_response.raise_for_status()
            
            with open(local_filepath, 'wb') as f:
                for chunk in logo_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            success_count += 1
        except requests.exceptions.RequestException:
            fail_count += 1

    print("\n--- Скачивание завершено! ---")
    print(f"✅ Успешно скачано: {success_count} логотипов.")
    if fail_count > 0:
        print(f"❌ Не удалось скачать: {fail_count} логотипов.")
    print(f"Все логотипы сохранены в папку: {LOCAL_LOGO_DIR}")

if __name__ == "__main__":
    # Убедитесь, что у вас установлены библиотеки: pip install requests tqdm
    download_logos()