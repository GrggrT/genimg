# translator.py
import deepl
from tkinter import messagebox
from config import DEEPL_API_KEY, DEEPL_TARGET_LANG_MAP, SOURCE_LANGUAGE_CODE

class TranslatorAPI:
    def __init__(self):
        self.translator = None
        try:
            self.translator = deepl.Translator(DEEPL_API_KEY)
            usage = self.translator.get_usage()
            if usage.any_limit_reached:
                print("Внимание: Достигнут лимит использования DeepL API.")
            else:
                print(f"DeepL API аутентифицирован. Использовано: {usage.character.count}/{usage.character.limit}")
        except Exception as e:
            messagebox.showerror("DeepL Ошибка", f"Не удалось инициализировать DeepL: {e}\nПеревод будет недоступен.")

    def translate(self, text, target_lang_code):
        if not self.translator or not text or not text.strip() or target_lang_code.upper() == SOURCE_LANGUAGE_CODE:
            return text

        target_lang = DEEPL_TARGET_LANG_MAP.get(target_lang_code.upper(), target_lang_code.upper())
        try:
            result = self.translator.translate_text(text, source_lang=SOURCE_LANGUAGE_CODE, target_lang=target_lang)
            return result.text
        except Exception as e:
            print(f"Ошибка перевода DeepL для '{text}' на {target_lang}: {e}")
            return text