# main.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)
# Главный файл для запуска приложения.
# Содержит основную логику управления процессом генерации.

import os
from tkinter import messagebox
import gui
import image_generator
from translator import TranslatorAPI # ИСПРАВЛЕНИЕ: Импортируем класс с правильным именем
from config import LOGO_DIR, TARGET_LANGUAGES, SOURCE_LANGUAGE_CODE

def start_generation_process(all_posts_data, gui_root_window):
    """
    Основная управляющая функция. Запускается из GUI.
    """
    if not all_posts_data:
        messagebox.showerror("Ошибка", "Список постов для генерации пуст!")
        return

    gui_root_window.destroy() # Закрываем GUI перед началом долгого процесса
    
    # ИСПРАВЛЕНИЕ: Создаем объект класса с правильным именем
    translator_instance = TranslatorAPI() 

    for post_idx, original_post_data in enumerate(all_posts_data):
        post_type = original_post_data["post_type"]
        bg_path = original_post_data.get("background_path", "")
        
        for lang_code in TARGET_LANGUAGES:
            print(f"\n--- Генерация поста {post_idx+1} ({post_type}), Язык: {lang_code} ---")
            
            # --- Одиночный прогноз ---
            if post_type == "Одиночный прогноз":
                translated_content = {
                    "team1": {"name": original_post_data["team1"]["name"], "logo": original_post_data["team1"]["logo_ref"]},
                    "team2": {"name": original_post_data["team2"]["name"], "logo": original_post_data["team2"]["logo_ref"]},
                    "vs_text": original_post_data["vs_text"],
                    "coefficient": original_post_data["coefficient"],
                    "prediction": original_post_data["prediction"],
                    "date": original_post_data["date"],
                    "background_path": bg_path
                }
                translated_content["team1"]["name"] = translator_instance.translate(original_post_data["team1"]["name"], lang_code)
                translated_content["team2"]["name"] = translator_instance.translate(original_post_data["team2"]["name"], lang_code)
                translated_content["vs_text"] = translator_instance.translate(original_post_data["vs_text"], lang_code)
                translated_content["prediction"] = translator_instance.translate(original_post_data["prediction"], lang_code)
                
                output_filename = f'single_post_{post_idx+1}_{lang_code.lower()}.jpg'
                
                # Вызываем функцию с правильным именем, которое уже было исправлено ранее
                image_generator.create_single_image(translated_content, bg_path, output_filename)

            # --- Экспресс ---
            elif post_type == "Экспресс":
                translated_legs = []
                for leg in original_post_data["legs"]:
                    translated_leg = leg.copy()
                    translated_leg["team1_name"] = translator_instance.translate(leg["team1_name"], lang_code)
                    translated_leg["team2_name"] = translator_instance.translate(leg["team2_name"], lang_code)
                    translated_leg["bet_text"] = translator_instance.translate(leg["bet_text"], lang_code)
                    translated_legs.append(translated_leg)
                
                translated_content = {
                    "express_title": translator_instance.translate(original_post_data["express_title"], lang_code),
                    "total_coefficient": original_post_data["total_coefficient"],
                    "date": original_post_data["date"],
                    "legs": translated_legs,
                    "background_path": bg_path
                }
                
                output_filename = f'express_post_{post_idx+1}_{lang_code.lower()}.jpg'
                
                # Вызываем функцию-заглушку для отрисовки экспресса
                image_generator.create_express_image(translated_content, bg_path, output_filename)
                
    print("\n--- Генерация всех изображений завершена! ---")
    messagebox.showinfo("Завершено", "Генерация всех изображений успешно завершена!")


if __name__ == "__main__":
    if not os.path.exists(LOGO_DIR):
        try:
            os.makedirs(LOGO_DIR)
            print(f"Папка для логотипов создана: {LOGO_DIR}")
        except OSError as e:
            messagebox.showerror("Ошибка папки", f"Не удалось создать папку для логотипов: {LOGO_DIR}\n{e}")
            if not messagebox.askyesno("Продолжить?", "Продолжить без возможности использовать логотипы?"):
                exit()
    
    # Запускаем GUI и передаем ему callback-функцию для старта генерации
    gui.create_main_gui(on_generate_callback=start_generation_process)