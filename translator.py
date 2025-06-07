import deepl
from tkinter import messagebox
from config import DEEPL_API_KEY

class Translator:
    def __init__(self):
        self.translator = None
        self._initialize_translator()

    def _initialize_translator(self):
        try:
            self.translator = deepl.Translator(DEEPL_API_KEY)
            usage = self.translator.get_usage()
            if usage.any_limit_reached:
                print("Внимание: Достигнут лимит использования DeepL API.")
                messagebox.showwarning("DeepL Лимит", "Достигнут лимит использования DeepL API. Перевод может быть неполным.")
            else:
                print(f"DeepL API аутентифицирован. Использовано символов: {usage.character.count} из {usage.character.limit or 'безлимитно'}")
        except deepl.exceptions.AuthorizationException as auth_err:
            print(f"Ошибка аутентификации DeepL: {auth_err}")
            messagebox.showerror("DeepL Ошибка", f"Ошибка аутентификации DeepL: Неверный API ключ или проблемы с аккаунтом.\n{auth_err}\nФункция перевода будет недоступна.")
            self.translator = None
        except Exception as e:
            print(f"Ошибка инициализации DeepL Translator: {e}")
            messagebox.showerror("DeepL Ошибка", f"Не удалось инициализировать DeepL Translator: {e}\nФункция перевода будет недоступна.")
            self.translator = None

    def translate_text(self, text_to_translate, target_language_code, source_language_code="RU"):
        if not self.translator or not text_to_translate or not text_to_translate.strip():
            return text_to_translate

        if target_language_code.upper() == source_language_code.upper():
            return text_to_translate

        target_lang_for_api = target_language_code.upper()
        if target_lang_for_api == "EN":
            target_lang_for_api = "EN-US"
        if target_lang_for_api == "PT":
            target_lang_for_api = "PT-PT"

        try:
            print(f"DeepL: Перевод '{text_to_translate}' с {source_language_code} на {target_lang_for_api}")
            result = self.translator.translate_text(
                text_to_translate,
                source_lang=source_language_code,
                target_lang=target_lang_for_api
            )
            return result.text
        except deepl.exceptions.DeepLException as e:
            print(f"Ошибка перевода DeepL для '{text_to_translate}' на {target_lang_for_api}: {e}")
            return text_to_translate
        except Exception as e:
            print(f"Неожиданная ошибка при переводе '{text_to_translate}' на {target_lang_for_api}: {e}")
            return text_to_translate 