# gui.py
# Модуль, отвечающий за графический интерфейс (Tkinter).

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os

# Импортируем нужные функции и данные из других модулей
from config import LOGO_DIR, MAX_POSTS_IN_LIST, MAX_LEGS_IN_EXPRESS
try:
    from team_mappings_fixed import TEAM_MAPPINGS
except ImportError:
    messagebox.showerror("Ошибка импорта", "Файл team_mappings_fixed.py не найден или TEAM_MAPPINGS не определен.")
    TEAM_MAPPINGS = {}

# Глобальные переменные для состояния GUI
match_data_list = [] 
current_express_legs_buffer = []

def create_main_gui(on_generate_callback):
    root = tk.Tk()
    root.title("Генератор постов v0.5")
    root.geometry("700x850")
    
    # --- Секция выбора типа поста ---
    post_type_outer_frame = ttk.Frame(root, padding="10")
    post_type_outer_frame.pack(pady=5, padx=10, fill="x")
    ttk.Label(post_type_outer_frame, text="Выберите тип поста:").pack(side=tk.LEFT, padx=(0,10))
    post_type_var = tk.StringVar(value="Одиночный прогноз")
    post_type_combo = ttk.Combobox(post_type_outer_frame, textvariable=post_type_var, values=["Одиночный прогноз", "Экспресс"], state="readonly", width=25)
    post_type_combo.pack(side=tk.LEFT)
    
    # --- Контейнер для основных форм ввода ---
    input_forms_container = ttk.Frame(root, padding="5")
    input_forms_container.pack(pady=5, padx=10, fill="both", expand=True)

    single_post_frame = ttk.Frame(input_forms_container, padding="10")
    express_post_frame = ttk.Frame(input_forms_container, padding="10")

    # Словари для хранения виджетов
    single_entries = {}
    express_general_entries = {}
    express_leg_entries = {}
    team_names_for_combobox = sorted([name.capitalize() for name in TEAM_MAPPINGS.keys() if isinstance(name, str) and any(c.isalpha() for c in name)])

    # --- Вспомогательные функции, определенные до их использования ---
    def select_background_file_action(entry_widget):
        filepath = filedialog.askopenfilename(title="Выберите фон", filetypes=(("Изображения", "*.jpg *.jpeg *.png"),("Все файлы", "*.*")))
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def update_combobox_filter(entry_widget, all_options):
        current_text = entry_widget.get().lower()
        if current_text:
            filtered_options = [opt for opt in all_options if current_text in opt.lower()]
            entry_widget['values'] = filtered_options if filtered_options else all_options
        else:
            entry_widget['values'] = all_options

    # --- Поля для ОДИНОЧНОГО прогноза ---
    single_fields_config = [
        ("Название команды 1", "team1_name", "Combobox_Team"),
        ("Название команды 2", "team2_name", "Combobox_Team"),
        ("Текст VS", "vs_text", "Entry"),
        ("Коэффициент", "coefficient", "Entry"),
        ("Прогноз", "prediction", "Entry_Large"),
        ("Дата", "date_single", "Entry"),
        ("Фон", "background_path_single", "Entry_File")
    ]
    for i, (label_text, key, widget_type) in enumerate(single_fields_config):
        label = ttk.Label(single_post_frame, text=label_text + ":")
        label.grid(row=i, column=0, padx=5, pady=6, sticky="w")
        if widget_type == "Combobox_Team":
            widget = ttk.Combobox(single_post_frame, width=35, values=team_names_for_combobox, state="normal")
            widget.bind('<KeyRelease>', lambda ev, e=widget, o=team_names_for_combobox: update_combobox_filter(e,o))
        elif widget_type == "Entry_File":
            widget = ttk.Entry(single_post_frame, width=38)
            browse_btn = ttk.Button(single_post_frame, text="Обзор...", command=lambda e=widget: select_background_file_action(e))
            browse_btn.grid(row=i, column=2, padx=(0,5), pady=6, sticky="w")
        else:
            widget = ttk.Entry(single_post_frame, width=38)
        widget.grid(row=i, column=1, padx=5, pady=6, sticky="ew")
        single_entries[key] = widget
    
    if "vs_text" in single_entries: single_entries["vs_text"].insert(0, "VS")
    if "date_single" in single_entries: single_entries["date_single"].insert(0, datetime.date.today().strftime("%d.%m.%Y"))
    
    # --- Поля для ЭКСПРЕССА ---
    express_general_fields_config = [
        ("Заголовок экспресса (необяз.)", "express_title", "Entry"),
        ("Общий коэффициент экспресса", "total_coefficient", "Entry"),
        ("Дата экспресса", "date_express", "Entry"),
        ("Фон для экспресса", "background_path_express", "Entry_File")
    ]
    for i, (label_text, key, widget_type) in enumerate(express_general_fields_config):
        label = ttk.Label(express_post_frame, text=label_text + ":")
        label.grid(row=i, column=0, padx=5, pady=6, sticky="w")
        if widget_type == "Entry_File":
            widget = ttk.Entry(express_post_frame, width=38)
            browse_btn = ttk.Button(express_post_frame, text="Обзор...", command=lambda e=widget: select_background_file_action(e))
            browse_btn.grid(row=i, column=2, padx=(0,5), pady=6, sticky="w")
        else:
            widget = ttk.Entry(express_post_frame, width=38)
        widget.grid(row=i, column=1, padx=5, pady=6, sticky="ew")
        express_general_entries[key] = widget
    if "date_express" in express_general_entries: express_general_entries["date_express"].insert(0, datetime.date.today().strftime("%d.%m.%Y"))
    
    leg_frame = ttk.LabelFrame(express_post_frame, text="Добавить событие в экспресс", padding="10")
    leg_frame.grid(row=len(express_general_fields_config), column=0, columnspan=3, pady=10, sticky="ew")
    leg_fields_config = [("Команда 1", "leg_team1_name", "Combobox_Team"), ("Команда 2", "leg_team2_name", "Combobox_Team"), ("Ставка", "leg_bet_text", "Entry"), ("Коэфф.", "leg_coefficient", "Entry")]
    for i, (label_text, key, widget_type) in enumerate(leg_fields_config):
        label = ttk.Label(leg_frame, text=label_text + ":")
        label.grid(row=i, column=0, padx=5, pady=4, sticky="w")
        if widget_type == "Combobox_Team":
            widget = ttk.Combobox(leg_frame, width=30, values=team_names_for_combobox, state="normal")
            widget.bind('<KeyRelease>', lambda ev, e=widget, o=team_names_for_combobox: update_combobox_filter(e,o))
        else:
            widget = ttk.Entry(leg_frame, width=33)
        widget.grid(row=i, column=1, padx=5, pady=4, sticky="ew")
        express_leg_entries[key] = widget

    add_leg_button = ttk.Button(leg_frame, text="➕ Добавить событие", command=lambda: add_leg_to_ui_buffer())
    add_leg_button.grid(row=len(leg_fields_config), column=0, columnspan=2, pady=10)
    
    legs_display_frame = ttk.LabelFrame(express_post_frame, text=f"События в экспрессе (макс. {MAX_LEGS_IN_EXPRESS})", padding="10")
    legs_display_frame.grid(row=len(express_general_fields_config)+1, column=0, columnspan=3, pady=10, sticky="ew")
    columns = ("#", "team1", "team2", "bet", "coeff")
    legs_treeview = ttk.Treeview(legs_display_frame, columns=columns, show="headings", height=5)
    legs_treeview.heading("#", text="№"); legs_treeview.column("#", width=30, anchor='center')
    legs_treeview.heading("team1", text="Команда 1"); legs_treeview.column("team1", width=120)
    legs_treeview.heading("team2", text="Команда 2"); legs_treeview.column("team2", width=120)
    legs_treeview.heading("bet", text="Ставка"); legs_treeview.column("bet", width=150)
    legs_treeview.heading("coeff", text="Коэфф."); legs_treeview.column("coeff", width=70, anchor='center')
    legs_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(legs_display_frame, orient="vertical", command=legs_treeview.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    legs_treeview.configure(yscrollcommand=scrollbar.set)
    
    remove_leg_button = ttk.Button(express_post_frame, text="➖ Удалить выбранное событие", command=lambda: remove_selected_leg_from_ui_buffer())
    remove_leg_button.grid(row=len(express_general_fields_config)+2, column=0, columnspan=3, pady=5)
    
    status_frame = ttk.Frame(root, padding="10")
    status_frame.pack(pady=10, padx=10, fill="x")
    match_count_list_label = ttk.Label(status_frame, text="Добавлено постов в список: 0")
    match_count_list_label.pack(side=tk.LEFT)
    
    action_buttons_frame = ttk.Frame(root, padding="10")
    action_buttons_frame.pack(pady=10, padx=10, fill="x")
    main_add_button = ttk.Button(action_buttons_frame, text="Добавить 'Одиночный прогноз' в список", command=lambda: add_current_post_to_list())
    main_add_button.pack(side=tk.LEFT, padx=5, expand=True, fill="x")
    generate_all_button = ttk.Button(action_buttons_frame, text="Создать все изображения", command=lambda: on_generate_callback(match_data_list, root))
    generate_all_button.pack(side=tk.LEFT, padx=5, expand=True, fill="x")
    
    example_button_single = ttk.Button(single_post_frame, text="Заполнить пример", command=lambda: fill_with_single_example())
    example_button_single.grid(row=len(single_fields_config), column=0, columnspan=2, pady=10)
    example_button_express = ttk.Button(express_general_entries["express_title"].master, text="Заполнить пример", command=lambda: fill_with_express_example())
    example_button_express.grid(row=len(express_general_fields_config), column=0, columnspan=2, pady=20)

    # --- Функции логики GUI ---
    def update_legs_treeview():
        for i in legs_treeview.get_children(): legs_treeview.delete(i)
        for idx, leg_data in enumerate(current_express_legs_buffer): legs_treeview.insert("", "end", iid=str(idx), values=(idx + 1, leg_data["team1_name"], leg_data["team2_name"], leg_data["bet_text"], leg_data["leg_coefficient"]))

    def on_post_type_change_ui(event=None):
        global current_express_legs_buffer; current_express_legs_buffer = []; update_legs_treeview()
        selected_type = post_type_var.get()
        if selected_type == "Одиночный прогноз": single_post_frame.pack(fill="both", expand=True); express_post_frame.pack_forget(); main_add_button.config(text="Добавить 'Одиночный прогноз' в список")
        elif selected_type == "Экспресс": single_post_frame.pack_forget(); express_post_frame.pack(fill="both", expand=True); main_add_button.config(text="Добавить 'Экспресс' в список")

    def get_logo_ref_for_team(team_name_original):
        team_name_lower = team_name_original.lower()
        logo_filename = TEAM_MAPPINGS.get(team_name_lower)
        if logo_filename:
            full_logo_path = os.path.join(LOGO_DIR, logo_filename)
            if os.path.exists(full_logo_path):
                print(f"ОК: Логотип для '{team_name_original}' найден: {full_logo_path}")
                return full_logo_path
        print(f"ПРЕДУПРЕЖДЕНИЕ: Логотип для '{team_name_original}' не найден. Используется плейсхолдер.")
        return team_name_original

    def add_leg_to_ui_buffer():
        if len(current_express_legs_buffer) >= MAX_LEGS_IN_EXPRESS: messagebox.showwarning("Лимит", f"Максимум {MAX_LEGS_IN_EXPRESS} событий."); return
        team1_name = express_leg_entries["leg_team1_name"].get().strip(); team2_name = express_leg_entries["leg_team2_name"].get().strip(); bet_text = express_leg_entries["leg_bet_text"].get().strip(); leg_coeff = express_leg_entries["leg_coefficient"].get().strip()
        if not (team1_name and team2_name and bet_text and leg_coeff): messagebox.showerror("Ошибка", "Заполните все поля события!"); return
        try: float(leg_coeff.replace(',', '.'))
        except ValueError: messagebox.showerror("Ошибка", "Коэфф. события должен быть числом!"); return
        team1_logo_ref = get_logo_ref_for_team(team1_name); team2_logo_ref = get_logo_ref_for_team(team2_name)
        current_express_legs_buffer.append({"team1_name": team1_name, "team1_logo_ref": team1_logo_ref, "team2_name": team2_name, "team2_logo_ref": team2_logo_ref, "bet_text": bet_text, "leg_coefficient": leg_coeff})
        update_legs_treeview(); express_leg_entries["leg_team1_name"].set(''); express_leg_entries["leg_team2_name"].set(''); express_leg_entries["leg_bet_text"].delete(0, tk.END); express_leg_entries["leg_coefficient"].delete(0, tk.END); express_leg_entries["leg_team1_name"].focus()

    def remove_selected_leg_from_ui_buffer():
        selected_items = legs_treeview.selection()
        if not selected_items: messagebox.showinfo("Информация", "Выберите событие для удаления."); return
        try:
            selected_idx = int(selected_items[0])
            if 0 <= selected_idx < len(current_express_legs_buffer): del current_express_legs_buffer[selected_idx]; update_legs_treeview()
            else: messagebox.showerror("Ошибка", "Некорректный индекс для удаления.")
        except (ValueError, IndexError): messagebox.showerror("Ошибка", "Не удалось удалить элемент.")

    def add_current_post_to_list():
        post_type = post_type_var.get(); final_post_data = {"post_type": post_type}
        if post_type == "Одиночный прогноз":
            team1_name = single_entries["team1_name"].get().strip(); team2_name = single_entries["team2_name"].get().strip()
            if not (team1_name and team2_name): messagebox.showerror("Ошибка", "Укажите обе команды!"); return
            team1_logo_ref = get_logo_ref_for_team(team1_name); team2_logo_ref = get_logo_ref_for_team(team2_name)
            final_post_data.update({"team1": {"name": team1_name, "logo_ref": team1_logo_ref}, "team2": {"name": team2_name, "logo_ref": team2_logo_ref}, "vs_text": single_entries["vs_text"].get() or "VS", "coefficient": single_entries["coefficient"].get(), "prediction": single_entries["prediction"].get(), "date": single_entries["date_single"].get() or datetime.date.today().strftime("%d.%m.%Y"), "background_path": single_entries["background_path_single"].get().strip()})
            for key in ["team1_name", "team2_name", "coefficient", "prediction"]:
                 if key in single_entries: single_entries[key].delete(0, tk.END)
            single_entries["team1_name"].focus()
        elif post_type == "Экспресс":
            if not current_express_legs_buffer: messagebox.showerror("Ошибка", "Добавьте хотя бы одно событие!"); return
            total_coeff_str = express_general_entries["total_coefficient"].get().strip()
            if not total_coeff_str: messagebox.showerror("Ошибка", "Укажите общий коэфф.!"); return
            try: float(total_coeff_str.replace(',','.'))
            except ValueError: messagebox.showerror("Ошибка", "Общий коэфф. должен быть числом!"); return
            final_post_data.update({"express_title": express_general_entries["express_title"].get().strip(), "total_coefficient": total_coeff_str, "date": express_general_entries["date_express"].get() or datetime.date.today().strftime("%d.%m.%Y"), "legs": list(current_express_legs_buffer), "background_path": express_general_entries["background_path_express"].get().strip()})
            current_express_legs_buffer.clear(); update_legs_treeview()
            for key in ["express_title", "total_coefficient"]:
                if key in express_general_entries: express_general_entries[key].delete(0, tk.END)
            express_leg_entries["leg_team1_name"].focus()
        match_data_list.append(final_post_data); match_count_list_label.config(text=f"Добавлено постов в список: {len(match_data_list)}")
    
    def fill_with_single_example():
        for key in ["team1_name", "team2_name", "coefficient", "prediction"]:
            if key in single_entries: single_entries[key].delete(0, tk.END)
        single_entries["team1_name"].set("Спартак"); single_entries["team2_name"].set("Зенит")
        single_entries["coefficient"].insert(0, "2.55"); single_entries["prediction"].insert(0, "Победа Спартака или ничья (1X)")

    def fill_with_express_example():
        global current_express_legs_buffer; current_express_legs_buffer = []
        for key in ["express_title", "total_coefficient"]:
            if key in express_general_entries: express_general_entries[key].delete(0, tk.END)
        express_general_entries["express_title"].insert(0, "Экспресс на выходные"); express_general_entries["total_coefficient"].insert(0, "7.45")
        example_legs = [
            {"team1_name": "Реал Мадрид", "team1_logo_ref": TEAM_MAPPINGS.get("real madrid", "Реал Мадрид"), "team2_name": "Барселона", "team2_logo_ref": TEAM_MAPPINGS.get("барселона", "Барселона"), "bet_text": "Обе забьют - Да", "leg_coefficient": "1.65"},
            {"team1_name": "Ливерпуль", "team1_logo_ref": TEAM_MAPPINGS.get("ливерпуль", "Ливерпуль"), "team2_name": "Манчестер Сити", "team2_logo_ref": TEAM_MAPPINGS.get("манчестер сити", "Манчестер Сити"), "bet_text": "Тотал Больше 2.5", "leg_coefficient": "1.70"},
            {"team1_name": "Бавария", "team1_logo_ref": TEAM_MAPPINGS.get("бавария", "Бавария"), "team2_name": "Боруссия Д", "team2_logo_ref": TEAM_MAPPINGS.get("дортмунд", "Боруссия Д"), "bet_text": "П1", "leg_coefficient": "1.50"}
        ]
        current_express_legs_buffer.extend(example_legs[:MAX_LEGS_IN_EXPRESS]); update_legs_treeview()
    
    post_type_combo.bind("<<ComboboxSelected>>", on_post_type_change_ui)
    on_post_type_change_ui()
    root.mainloop()