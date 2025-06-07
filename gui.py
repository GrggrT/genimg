import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
from config import (
    LOGO_DIR, DEFAULT_VS_TEXT, DEFAULT_DATE_FORMAT,
    MAX_MATCHES, TRANSLATABLE_FIELDS, TARGET_LANGUAGES
)
from image_generator import create_single_image_for_match_data
from translator import Translator

class MatchGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Создание изображений для Telegram")
        self.root.geometry("550x700")
        
        self.match_data = []
        self.translator = Translator()
        
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create entry fields
        self.fields = [
            ("Название команды 1", "team1_name", True),
            ("Название команды 2", "team2_name", True),
            ("Текст VS", "vs_text", False),
            ("Коэффициент", "coefficient", False),
            ("Прогноз", "prediction", False),
            ("Дата (пусто = текущая)", "date", False),
            ("Фон (пусто = по умолч.)", "background_path", False)
        ]
        
        self.entries = {}
        self.team_names_for_combobox = sorted([
            name.capitalize() for name in self._get_team_mappings().keys()
            if isinstance(name, str) and any(c.isalpha() for c in name)
        ])
        
        for i, (label_text, field_key, is_combobox) in enumerate(self.fields):
            label = ttk.Label(self.main_frame, text=label_text + ":")
            label.grid(row=i, column=0, padx=5, pady=8, sticky="w")
            
            if is_combobox:
                entry = ttk.Combobox(self.main_frame, width=35, values=self.team_names_for_combobox, state="normal")
                entry.bind('<KeyRelease>', lambda e, entry=entry: self._update_combobox_filter(entry))
                entry.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
            else:
                entry = ttk.Entry(self.main_frame, width=38)
                entry.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
                if field_key == "background_path":
                    browse_button = ttk.Button(
                        self.main_frame,
                        text="Обзор...",
                        command=lambda e=entry: self._select_background_file(e)
                    )
                    browse_button.grid(row=i, column=2, padx=(0,5), pady=8, sticky="w")
            
            self.entries[field_key] = entry
        
        # Set default values
        self.entries["vs_text"].insert(0, DEFAULT_VS_TEXT)
        self.entries["date"].insert(0, datetime.date.today().strftime(DEFAULT_DATE_FORMAT))
        
        # Create match count label
        self.match_count_label = ttk.Label(self.main_frame, text="Добавлено матчей: 0")
        self.match_count_label.grid(row=len(self.fields), column=0, columnspan=3, pady=10)
        
        # Create buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=len(self.fields)+1, column=0, columnspan=3, pady=10)
        
        ttk.Button(
            self.button_frame,
            text="Добавить матч",
            command=self._add_match_action
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            self.button_frame,
            text="Создать изображения",
            command=self._generate_images_action
        ).pack(side=tk.LEFT, padx=10)
    
    def _setup_layout(self):
        self.main_frame.columnconfigure(1, weight=1)
    
    def _get_team_mappings(self):
        try:
            from team_mappings_fixed import TEAM_MAPPINGS
            return TEAM_MAPPINGS
        except ImportError:
            messagebox.showerror(
                "Ошибка импорта",
                "Файл team_mappings_fixed.py не найден или TEAM_MAPPINGS не определен.\nБудут использованы заглушки."
            )
            return {"спартак": "spartak.png", "зенит": "zenit.png", "placeholder_team": "non_existent.png"}
    
    def _update_combobox_filter(self, entry_widget):
        current_text = entry_widget.get().lower()
        if current_text:
            filtered_options = [opt for opt in self.team_names_for_combobox if current_text in opt.lower()]
            entry_widget['values'] = filtered_options if filtered_options else self.team_names_for_combobox
        else:
            entry_widget['values'] = self.team_names_for_combobox
    
    def _select_background_file(self, entry_widget):
        filepath = filedialog.askopenfilename(
            title="Выберите фоновое изображение",
            filetypes=(
                ("Файлы изображений", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                ("Все файлы", "*.*")
            )
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
    
    def _add_match_action(self):
        if len(self.match_data) >= MAX_MATCHES:
            messagebox.showwarning("Лимит", "Максимум 10 матчей!")
            return
        
        team1_name_input = self.entries["team1_name"].get().strip()
        team2_name_input = self.entries["team2_name"].get().strip()
        
        if not team1_name_input or not team2_name_input:
            messagebox.showerror("Ошибка", "Укажите названия обеих команд!")
            return
        
        team_mappings = self._get_team_mappings()
        team1_name_lower = team1_name_input.lower()
        team2_name_lower = team2_name_input.lower()
        
        team1_logo_filename = team_mappings.get(team1_name_lower)
        team2_logo_filename = team_mappings.get(team2_name_lower)
        
        team1_final_logo_ref = team1_name_input
        if team1_logo_filename:
            team1_logo_path = os.path.join(LOGO_DIR, team1_logo_filename)
            if os.path.exists(team1_logo_path):
                team1_final_logo_ref = team1_logo_path
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Файл лого '{team1_name_input}' не найден: {team1_logo_path}"
                )
        else:
            messagebox.showwarning(
                "Предупреждение",
                f"Сопоставление для '{team1_name_input}' не найдено."
            )
        
        team2_final_logo_ref = team2_name_input
        if team2_logo_filename:
            team2_logo_path = os.path.join(LOGO_DIR, team2_logo_filename)
            if os.path.exists(team2_logo_path):
                team2_final_logo_ref = team2_logo_path
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Файл лого '{team2_name_input}' не найден: {team2_logo_path}"
                )
        else:
            messagebox.showwarning(
                "Предупреждение",
                f"Сопоставление для '{team2_name_input}' не найдено."
            )
        
        current_match = {
            "team1": {"name": team1_name_input, "logo_ref": team1_final_logo_ref},
            "team2": {"name": team2_name_input, "logo_ref": team2_final_logo_ref},
            "vs_text": self.entries["vs_text"].get() or DEFAULT_VS_TEXT,
            "coefficient": self.entries["coefficient"].get(),
            "prediction": self.entries["prediction"].get(),
            "date": self.entries["date"].get() or datetime.date.today().strftime(DEFAULT_DATE_FORMAT)
        }
        
        self.match_data.append(current_match)
        self.match_count_label.config(text=f"Добавлено матчей: {len(self.match_data)}")
        
        # Clear input fields
        for field_key in ["team1_name", "team2_name", "coefficient", "prediction"]:
            self.entries[field_key].delete(0, tk.END)
        self.entries["team1_name"].focus()
    
    def _generate_images_action(self):
        if not self.match_data:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один матч!")
            return
        
        custom_background_path = self.entries["background_path"].get().strip()
        self.root.destroy()
        
        for match_idx, original_match_item in enumerate(self.match_data):
            for lang_code in TARGET_LANGUAGES:
                print(f"\n--- Генерация для матча {match_idx+1}, Язык: {lang_code} ---")
                
                translated_match_content = {
                    "team1": {
                        "name": original_match_item["team1"]["name"],
                        "logo": original_match_item["team1"]["logo_ref"]
                    },
                    "team2": {
                        "name": original_match_item["team2"]["name"],
                        "logo": original_match_item["team2"]["logo_ref"]
                    },
                    "vs_text": original_match_item["vs_text"],
                    "coefficient": original_match_item["coefficient"],
                    "prediction": original_match_item["prediction"],
                    "date": original_match_item["date"]
                }
                
                if lang_code != "RU":
                    if not self.translator.translator:
                        print(f"Переводчик DeepL не доступен. Используется оригинальный текст для языка {lang_code}.")
                    else:
                        for field in TRANSLATABLE_FIELDS:
                            if field in ["team1_name", "team2_name"]:
                                team_key = field.split("_")[0]
                                translated_match_content[team_key]["name"] = self.translator.translate_text(
                                    original_match_item[team_key]["name"],
                                    lang_code
                                )
                            else:
                                translated_match_content[field] = self.translator.translate_text(
                                    original_match_item[field],
                                    lang_code
                                )
                
                output_img_filename = f'telegram_match_post_{match_idx+1}_{lang_code.lower()}.jpg'
                create_single_image_for_match_data(
                    match_content_for_image=translated_match_content,
                    background_image_path=custom_background_path,
                    output_filename=output_img_filename
                )
        
        print("\n--- Генерация всех изображений завершена! ---")
    
    def run(self):
        self.root.mainloop() 