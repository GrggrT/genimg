# team_mappings_fixed.py (НОВАЯ, ПРОСТАЯ И РАБОЧАЯ ВЕРСИЯ)
import os
from config import LOGO_DIR # Импортируем путь к логотипам из вашего конфига

def get_auto_mappings_from_folder():
    """
    Сканирует папку LOGO_DIR и создает базовый словарь сопоставлений.
    Ключ: имя файла без расширения, в нижнем регистре.
    Значение: полное имя файла.
    Например: {"real madrid": "Real Madrid.png"}
    """
    auto_mappings = {}
    if not os.path.isdir(LOGO_DIR):
        print(f"!!! ОШИБКА: Папка с логотипами не найдена по пути: {LOGO_DIR}")
        return auto_mappings
        
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    for filename in os.listdir(LOGO_DIR):
        if filename.lower().endswith(valid_extensions):
            team_name_key = os.path.splitext(filename)[0].lower()
            if team_name_key not in auto_mappings:
                auto_mappings[team_name_key] = filename
            
    print(f"Найдено {len(auto_mappings)} логотипов при автоматическом сканировании папки.")
    return auto_mappings

def get_manual_aliases():
    """
    Ваш словарь с ручными псевдонимами. 
    Здесь вы можете добавлять любые альтернативные названия для команд.
    Ключ - псевдоним в нижнем регистре, значение - точное имя файла логотипа.
    """
    aliases = {
        # Русские названия
        "спартак": "Spartak Moscow.png",
        "зенит": "Zenit St. Petersburg.png",
        "цска": "CSKA Moscow.png",
        "локомотив": "Lokomotiv Moscow.png",
        "реал мадрид": "Real Madrid.png",
        "барселона": "FC Barcelona.png",
        "барса": "FC Barcelona.png",
        "ливерпуль": "Liverpool FC.png",
        "манчестер сити": "Manchester City.png",
        "твенте": "Twente Enschede FC.png", # Добавил пример из вашего скриншота

        # Примеры других псевдонимов
        "мю": "Manchester United.png",
        "man united": "Manchester United.png",
        "man city": "Manchester City.png",
        
        # ... Добавьте сюда любые другие псевдонимы, которые вам нужны ...
    }
    print(f"Загружено {len(aliases)} ручных псевдонимов.")
    return aliases

def create_final_mappings():
    """
    Объединяет все сопоставления. Ручные псевдонимы имеют приоритет.
    """
    auto_generated = get_auto_mappings_from_folder()
    manual = get_manual_aliases()
    
    # Сначала автоматические, потом ручные. 
    # Если ключ совпадет, значение из ручного словаря перезапишет автоматическое.
    final_mappings = {**auto_generated, **manual}
    
    print(f"Сформирован итоговый словарь TEAM_MAPPINGS из {len(final_mappings)} уникальных записей.")
    return final_mappings

# --- Итоговый словарь, который будет импортироваться в другие модули ---
TEAM_MAPPINGS = create_final_mappings()