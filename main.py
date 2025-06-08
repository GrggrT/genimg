# main.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)
import os
from tkinter import messagebox
from gui import MatchGeneratorGUI
import image_generator
from translator import Translator
from config import LOGO_DIR, TARGET_LANGUAGES

def main():
    """
    Главная функция для запуска приложения.
    """
    app = MatchGeneratorGUI()
    
    def start_generation_process(all_posts_data, gui_root_window):
        if not all_posts_data:
            messagebox.showerror("Ошибка", "Список постов для генерации пуст!")
            return
        
        gui_root_window.destroy()
        translator_instance = Translator()
        
        output_folder = os.getcwd() # Папка, куда будут сохраняться изображения

        for post_idx, original_post_data in enumerate(all_posts_data):
            post_type = original_post_data.get("post_type", "Одиночный прогноз")
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
                    if lang_code != "RU":
                        for field in ["team1", "team2"]:
                            translated_content[field]["name"] = translator_instance.translate_text(original_post_data[field]["name"], lang_code)
                        for field in ["vs_text", "prediction"]:
                            translated_content[field] = translator_instance.translate_text(original_post_data[field], lang_code)
                    
                    output_filename = f'single_post_{post_idx+1}_{lang_code.lower()}.jpg'
                    
                    # ИСПРАВЛЕНИЕ: Вызываем функцию с правильным именем
                    image_generator.draw_single_match_post(
                        post_data=translated_content,
                        output_folder=output_folder,
                        filename=output_filename
                    )

                # --- Экспресс ---
                elif post_type == "Экспресс":
                    # Логика для экспресса (пока использует заглушку)
                    # ... (здесь будет ваша логика перевода для экспрессов)
                    
                    output_filename = f'express_post_{post_idx+1}_{lang_code.lower()}.jpg'
                    
                    # ИСПРАВЛЕНИЕ: Вызываем функцию с правильным именем
                    image_generator.draw_express_post(
                        post_data=original_post_data, # Пока передаем оригинал в заглушку
                        output_folder=output_folder,
                        filename=output_filename
                    )
        
        print("\n--- Генерация всех изображений завершена! ---")
        messagebox.showinfo("Завершено", "Генерация всех изображений успешно завершена!")

    # Запускаем GUI и передаем ему callback-функцию
    app.run(on_generate_callback=start_generation_process)


if __name__ == "__main__":
    if not os.path.exists(LOGO_DIR):
        try:
            os.makedirs(LOGO_DIR)
            print(f"Папка для логотипов создана: {LOGO_DIR}")
        except OSError as e:
            messagebox.showerror("Ошибка папки", f"Не удалось создать папку для логотипов: {LOGO_DIR}\n{e}")
            if not messagebox.askyesno("Продолжить?", "Продолжить без возможности использовать логотипы?"):
                exit()
    
    main()