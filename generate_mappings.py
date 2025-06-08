# generate_mappings.py
# Этот скрипт нужно запустить ОДИН РАЗ после скачивания всех логотипов.
# Он автоматически создаст словарь с русскими псевдонимами.

import os
import deepl
from config import LOGO_DIR, DEEPL_API_KEY, SOURCE_LANGUAGE_CODE

def create_russian_aliases_from_folder():
    """
    Сканирует папку с логотипами, переводит их имена на русский
    и генерирует код для словаря псевдонимов.
    """
    # 1. Инициализация переводчика
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        print("DeepL API аутентифицирован.")
    except Exception as e:
        print(f"!!! Ошибка инициализации DeepL: {e}")
        print("!!! Убедитесь, что ваш API ключ в config.py верен и активен.")
        return

    # 2. Проверка папки с логотипами
    if not os.path.isdir(LOGO_DIR):
        print(f"!!! ОШИБКА: Папка с логотипами не найдена по пути: {LOGO_DIR}")
        return

    print(f"\nНачинаем генерацию русского словаря из папки {LOGO_DIR}...")
    
    generated_aliases = {}
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    
    # 3. Перебор всех файлов в папке
    logo_files = [f for f in os.listdir(LOGO_DIR) if f.lower().endswith(valid_extensions)]
    
    for filename in logo_files:
        # Получаем чистое английское имя
        english_name = os.path.splitext(filename)[0]
        # Ключ для словаря (имя файла в нижнем регистре без расширения)
        english_key = english_name.lower()
        
        # Переводим на русский
        # Используем Deepl для перевода с английского на русский
        try:
            result = translator.translate_text(english_name, source_lang="EN", target_lang=SOURCE_LANGUAGE_CODE)
            russian_name = result.text.lower()
            
            # Добавляем в словарь, если такого русского названия еще нет
            if russian_name not in generated_aliases:
                generated_aliases[russian_name] = english_key
                print(f"  '{russian_name}': '{english_key}',")
            
        except Exception as e:
            print(f"  # Ошибка перевода для '{english_name}': {e}")
            # В случае ошибки перевода, можно добавить английский ключ как псевдоним
            if english_key not in generated_aliases:
                generated_aliases[english_key] = english_key


    # 4. Формируем и выводим готовый код для вставки
    print("\n\n--- КОД СГЕНЕРИРОВАН ---")
    print("Скопируйте весь словарь ниже и вставьте его в файл team_mappings_fixed.py,")
    print("заменив существующий словарь RUSSIAN_TO_ENGLISH_ALIASES.\n")
    
    # Красиво форматируем вывод словаря
    output_code = "RUSSIAN_TO_ENGLISH_ALIASES = {\n"
    for key, value in sorted(generated_aliases.items()):
        output_code += f"    '{key}': '{value}',\n"
    output_code += "}"
    
    print(output_code)
    
    # Также сохраняем в файл для удобства
    with open("generated_aliases.txt", "w", encoding="utf-8") as f:
        f.write(output_code)
    print("\nКод также сохранен в файл 'generated_aliases.txt' в этой же папке.")


if __name__ == "__main__":
    # Убедитесь, что у вас установлена библиотека deepl: pip install deepl
    create_russian_aliases_from_folder()