# main.py (ЕДИНЫЙ И ИСПРАВЛЕННЫЙ ФАЙЛ)
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk

# --- 1. КОНФИГУРАЦИЯ (все настройки здесь) ---
try:
    from team_mappings_fixed import TEAM_MAPPINGS
except ImportError:
    messagebox.showerror("Критическая ошибка", "Файл team_mappings_fixed.py не найден. Пожалуйста, убедитесь, что он находится в той же папке.")
    TEAM_MAPPINGS = {}

LOGO_DIR = r"C:\1\logos"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
DEEPL_API_KEY = "8f34b9b3-a664-42ad-8e3c-c1a4e9ec748d:fx"
SOURCE_LANGUAGE_CODE = "RU"
TARGET_LANGUAGES = ["RU", "FR", "DE", "PL", "PT", "ES", "UK", "EN"]
DEEPL_TARGET_LANG_MAP = {"EN": "EN-US", "PT": "PT-PT"}
MAX_POSTS_IN_LIST = 10
MAX_LEGS_IN_EXPRESS = 10
IMAGE_SIZE = (1280, 1280)
DEFAULT_BACKGROUND_COLOR_1 = (28, 37, 38)
DEFAULT_BACKGROUND_COLOR_2 = (0, 0, 0)
IMAGE_QUALITY = 90

# --- 2. ЛОГИКА ПЕРЕВОДА (DeepL) ---
translator_instance = None
try:
    import deepl
    translator_instance = deepl.Translator(DEEPL_API_KEY)
    usage = translator_instance.get_usage()
    if usage.any_limit_reached: print("Внимание: Достигнут лимит использования DeepL API.")
    else: print(f"DeepL API аутентифицирован. Использовано: {usage.character.count}/{usage.character.limit}")
except ImportError:
    print("Библиотека deepl не установлена. Перевод будет недоступен. pip install deepl")
except Exception as e:
    messagebox.showerror("DeepL Ошибка", f"Не удалось инициализировать DeepL: {e}\nПеревод будет недоступен.")

def translate_text(text, target_lang):
    if not translator_instance or not text or not text.strip() or target_lang.upper() == SOURCE_LANGUAGE_CODE:
        return text
    target_lang_code = DEEPL_TARGET_LANG_MAP.get(target_lang.upper(), target_lang.upper())
    try:
        result = translator_instance.translate_text(text, source_lang=SOURCE_LANGUAGE_CODE, target_lang=target_lang_code)
        return result.text
    except Exception as e:
        print(f"Ошибка перевода DeepL для '{text}': {e}")
        return text

# --- 3. ЛОГИКА ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ (Pillow) ---

def get_font_for_cell(draw_context, text_to_fit, target_width, target_height, initial_font_size=40, min_font_size=10, max_lines=3):
    font_size = initial_font_size
    while font_size >= min_font_size:
        try: font = ImageFont.truetype(FONT_PATH, font_size)
        except IOError: return ImageFont.load_default(), [text_to_fit]
        words = text_to_fit.split(); lines = []; current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if draw_context.textlength(test_line, font=font) <= target_width:
                current_line = test_line
            else:
                if current_line: lines.append(current_line)
                current_line = word
        if current_line: lines.append(current_line)
        if not lines and text_to_fit: lines = [text_to_fit]
        
        block_bbox = draw_context.multiline_textbbox((0,0), "\n".join(lines), font=font, spacing=int(font_size*0.2))
        if len(lines) <= max_lines and (block_bbox[3] - block_bbox[1]) <= target_height:
            return font, lines
        font_size -= 1
    final_font = ImageFont.truetype(FONT_PATH, min_font_size)
    print(f"Предупреждение: Текст '{text_to_fit[:30]}...' не вписался идеально.")
    return final_font, lines

def draw_text_with_effects(draw, text_block, center_xy, font, color, shadow_color, stroke_color, is_multiline=False):
    x, y = center_xy
    align = "center" if is_multiline else "left"
    spacing = int(font.size * 0.2)
    if is_multiline: bbox = draw.multiline_textbbox((0,0), text_block, font=font, spacing=spacing, align=align)
    else: bbox = draw.textbbox((0,0), text_block, font=font)
    pos = (x - (bbox[2]-bbox[0]) / 2, y - (bbox[3]-bbox[1]) / 2)
    if shadow_color:
        if is_multiline: draw.multiline_text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color, spacing=spacing, align=align)
        else: draw.text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color)
    if is_multiline: draw.multiline_text(pos, text_block, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color, spacing=spacing, align=align)
    else: draw.text(pos, text_block, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color)

def create_gradient_bg(width, height, color1, color2):
    image = Image.new('RGB', (width, height)); draw = ImageDraw.Draw(image)
    r1,g1,b1=color1; r2,g2,b2=color2
    for i in range(height):
        r=int(r1+(r2-r1)*i/height); g=int(g1+(g2-g1)*i/height); b=int(b1+(b2-b1)*i/height)
        draw.line([(0,i), (width,i)], fill=(r,g,b))
    return image

def create_single_image(match_content, background_path, output_filename):
    # ... (код этой функции без изменений) ...
    image = None
    if background_path and os.path.exists(background_path):
        try: image = Image.open(background_path).convert("RGB").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        except Exception as e: print(f"Ошибка фона: {e}")
    if image is None: image = create_gradient_bg(IMAGE_SIZE[0], IMAGE_SIZE[1], DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2)
    draw = ImageDraw.Draw(image); padding = 15
    user_defined_cells = [{'type': 'team_name', 'x': 350, 'y': 200, 'w': 250, 'h': 70}, {'type': 'team_name', 'x': 950, 'y': 200, 'w': 250, 'h': 70}, {'type': 'logo', 'x': 350, 'y': 350, 'w': 200, 'h': 220}, {'type': 'logo', 'x': 950, 'y': 350, 'w': 200, 'h': 220}, {'type': 'vs_text', 'x': 650, 'y': 350, 'w': 100, 'h': 100}, {'type': 'coefficient', 'x': 650, 'y': 550, 'w': 150, 'h': 150}, {'type': 'prediction', 'x': 650, 'y': 870, 'w': 900, 'h': 300}, {'type': 'date', 'x': 650, 'y': 1150,'w': 200, 'h': 40}]
    content_map = [match_content["team1"]["name"], match_content["team2"]["name"], match_content["team1"]["logo"], match_content["team2"]["logo"], match_content["vs_text"], match_content["coefficient"], match_content["prediction"], match_content["date"]]
    for idx, cell in enumerate(user_defined_cells):
        content = str(content_map[idx]); is_multiline = False; font_params = {}; text_color = '#FFFFFF'; shadow = '#444444'; outline = '#000000'
        if cell['type'] == 'team_name': font_params = {'initial_font_size': 50, 'min_font_size': 18, 'max_lines': 3}; text_color = '#E0E0E0'
        elif cell['type'] == 'vs_text': font_params = {'initial_font_size': 60, 'min_font_size': 30, 'max_lines': 1}; text_color = '#FFD700'
        elif cell['type'] == 'coefficient': font_params = {'initial_font_size': 70, 'min_font_size': 30, 'max_lines': 1}; text_color = '#4CAF50'
        elif cell['type'] == 'prediction': font_params = {'initial_font_size': 45, 'min_font_size': 16, 'max_lines': 7}; text_color = '#FFFFFF'; is_multiline = True
        elif cell['type'] == 'date': font_params = {'initial_font_size': 35, 'min_font_size': 15, 'max_lines': 1}; text_color = '#AAAAAA'
        elif cell['type'] == 'logo':
            logo_path = content; team_name_placeholder = content_map[0] if idx == 2 else content_map[1]
            try:
                if os.path.exists(logo_path):
                    logo_img = Image.open(logo_path).convert("RGBA"); logo_img.thumbnail((cell['w'], cell['h']), Image.Resampling.LANCZOS)
                    pos_x = cell['x'] - logo_img.width // 2; pos_y = cell['y'] - logo_img.height // 2; shadow_pos = (pos_x + 3, pos_y + 3)
                    image.paste((50,50,50), [shadow_pos[0], shadow_pos[1], shadow_pos[0]+logo_img.width, shadow_pos[1]+logo_img.height])
                    image.paste(logo_img, (pos_x, pos_y), logo_img)
                else: 
                    draw.rectangle((cell['x']-cell['w']//2, cell['y']-cell['h']//2, cell['x']+cell['w']//2, cell['y']+cell['h']//2), fill=(70,70,70))
                    font_obj, lines = get_font_for_cell(draw, team_name_placeholder, cell['w']-2*padding, cell['h']-2*padding, initial_font_size=30, max_lines=3)
                    draw_text_with_effects(draw, "\n".join(lines), (cell['x'], cell['y']), font_obj, '#DDDDDD', shadow, outline, is_multiline=True)
            except Exception as e: print(f"Ошибка лого '{logo_path}': {e}")
            continue
        font, lines = get_font_for_cell(draw, content, cell['w']-2*padding, cell['h']-2*padding, **font_params)
        draw_text_with_effects(draw, "\n".join(lines), (cell['x'], cell['y']), font, text_color, shadow, outline, is_multiline=is_multiline or len(lines)>1)
    try: image.save(output_filename, quality=IMAGE_QUALITY); print(f"Создано изображение: {output_filename}")
    except Exception as e: print(f"Ошибка сохранения {output_filename}: {e}")

def create_express_image(express_content, background_path, output_filename):
    # ... (код этой функции без изменений) ...
    image = None
    if background_path and os.path.exists(background_path):
        try: image = Image.open(background_path).convert("RGB").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        except Exception as e: print(f"Ошибка фона: {e}")
    if image is None: image = create_gradient_bg(IMAGE_SIZE[0], IMAGE_SIZE[1], DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2)
    draw = ImageDraw.Draw(image); padding = 40
    header_y_pos = 100
    if express_content.get("express_title"):
        font_title, lines_title = get_font_for_cell(draw, express_content["express_title"], IMAGE_SIZE[0] - 2*padding, 100, initial_font_size=60, min_font_size=30, max_lines=2)
        draw_text_with_effects(draw, "\n".join(lines_title), (IMAGE_SIZE[0]/2, header_y_pos), font_title, '#FFD700', '#000000', '#000000', is_multiline=len(lines_title)>1)
        header_y_pos += len(lines_title) * (font_title.size * 1.2)
    font_date, _ = get_font_for_cell(draw, express_content["date"], 200, 40, initial_font_size=25, min_font_size=15, max_lines=1)
    draw_text_with_effects(draw, express_content["date"], (IMAGE_SIZE[0]/2, header_y_pos), font_date, '#AAAAAA', '#000000', '#000000')
    table_top_y = header_y_pos + 70; table_bottom_y = IMAGE_SIZE[1] - 200; table_height = table_bottom_y - table_top_y; table_width = IMAGE_SIZE[0] - 2 * padding
    legs = express_content.get("legs", []); num_legs = len(legs)
    if num_legs > 0:
        row_height = table_height / num_legs; col_widths_percent = {'match': 0.60, 'bet': 0.25, 'coeff': 0.15}; line_color = (255, 255, 255, 50)
        draw.line([(padding, table_top_y), (IMAGE_SIZE[0] - padding, table_top_y)], fill=line_color, width=2)
        draw.line([(padding, table_bottom_y), (IMAGE_SIZE[0] - padding, table_bottom_y)], fill=line_color, width=2)
        for i, leg in enumerate(legs):
            row_y_center = table_top_y + (i * row_height) + row_height / 2
            if i > 0: draw.line([(padding, table_top_y + i * row_height), (IMAGE_SIZE[0] - padding, table_top_y + i * row_height)], fill=line_color, width=1)
            col_match_width = table_width * col_widths_percent['match']; col_match_x_start = padding
            logo_h = int(row_height * 0.55); logo_w = logo_h; logo_y_pos = int(row_y_center - logo_h / 2)
            try:
                if os.path.exists(leg["team1_logo_ref"]):
                    logo1 = Image.open(leg["team1_logo_ref"]).convert("RGBA"); logo1.thumbnail((logo_w, logo_h), Image.Resampling.LANCZOS)
                    image.paste(logo1, (int(col_match_x_start + padding), logo_y_pos), logo1)
                if os.path.exists(leg["team2_logo_ref"]):
                    logo2 = Image.open(leg["team2_logo_ref"]).convert("RGBA"); logo2.thumbnail((logo_w, logo_h), Image.Resampling.LANCZOS)
                    image.paste(logo2, (int(col_match_x_start + col_match_width - logo_w - padding), logo_y_pos), logo2)
            except Exception as e: print(f"Ошибка лого в экспрессе: {e}")
            teams_text = f"{leg['team1_name']}\nVS\n{leg['team2_name']}"
            teams_text_width_target = col_match_width - 2*logo_w - 4*padding
            font_teams, lines_teams = get_font_for_cell(draw, teams_text, teams_text_width_target, row_height*0.8, initial_font_size=30, min_font_size=12, max_lines=3)
            draw_text_with_effects(draw, "\n".join(lines_teams), (col_match_x_start + col_match_width/2, row_y_center), font_teams, '#FFFFFF', '#000000', '#000000', is_multiline=True)
            col_bet_width = table_width * col_widths_percent['bet']; col_bet_x_center = col_match_x_start + col_match_width + col_bet_width/2
            bet_text = leg['bet_text']; font_bet, lines_bet = get_font_for_cell(draw, bet_text, col_bet_width - padding, row_height*0.8, initial_font_size=28, min_font_size=12, max_lines=3)
            draw_text_with_effects(draw, "\n".join(lines_bet), (col_bet_x_center, row_y_center), font_bet, '#E0E0E0', '#000000', '#000000', is_multiline=len(lines_bet)>1)
            col_coeff_width = table_width * col_widths_percent['coeff']; col_coeff_x_center = col_match_x_start + col_match_width + col_bet_width + col_coeff_width/2
            coeff_text = leg['leg_coefficient']; font_coeff, _ = get_font_for_cell(draw, coeff_text, col_coeff_width - padding, row_height*0.8, initial_font_size=35, min_font_size=16, max_lines=1)
            draw_text_with_effects(draw, coeff_text, (col_coeff_x_center, row_y_center), font_coeff, '#4CAF50', '#000000', '#000000')
    footer_y_pos = table_bottom_y + (IMAGE_SIZE[1] - table_bottom_y) / 2
    total_coeff_text = f"Общий коэффициент: {express_content['total_coefficient']}"; font_total_coeff, _ = get_font_for_cell(draw, total_coeff_text, table_width, 100, initial_font_size=50, min_font_size=25, max_lines=1)
    draw_text_with_effects(draw, total_coeff_text, (IMAGE_SIZE[0]/2, footer_y_pos), font_total_coeff, '#FFD700', '#000000', '#000000')
    try: image.save(output_filename, quality=IMAGE_QUALITY); print(f"Создано изображение (экспресс): {output_filename}")
    except Exception as e: print(f"Ошибка сохранения {output_filename}: {e}")

# --- 4. ЛОГИКА GUI И УПРАВЛЕНИЕ ---

match_data_list = [] 
current_express_legs_buffer = []

class MainApplication:
    def __init__(self, root):
        # ... (здесь весь код вашего GUI из файла gui.py) ...
        # (я скопировал его, внеся исправления)
        self.root = root
        self.root.title("Генератор постов v0.8")
        self.root.geometry("750x850")
        
        # --- Секция выбора типа поста ---
        post_type_outer_frame = ttk.Frame(root, padding="10"); post_type_outer_frame.pack(pady=5, padx=10, fill="x")
        ttk.Label(post_type_outer_frame, text="Выберите тип поста:").pack(side=tk.LEFT, padx=(0,10))
        self.post_type_var = tk.StringVar(value="Одиночный прогноз")
        post_type_combo = ttk.Combobox(post_type_outer_frame, textvariable=self.post_type_var, values=["Одиночный прогноз", "Экспресс"], state="readonly", width=25)
        post_type_combo.pack(side=tk.LEFT)
        post_type_combo.bind("<<ComboboxSelected>>", self.on_post_type_change_ui)

        # --- Контейнер для основных форм ввода ---
        self.input_forms_container = ttk.Frame(root, padding="5"); self.input_forms_container.pack(pady=5, padx=10, fill="both", expand=True)
        self.single_post_frame = ttk.Frame(self.input_forms_container, padding="10")
        self.express_post_frame = ttk.Frame(self.input_forms_container, padding="10")

        self.single_entries = {}; self.express_general_entries = {}; self.express_leg_entries = {}
        self.team_names_for_combobox = sorted([name.capitalize() for name in TEAM_MAPPINGS.keys() if isinstance(name, str) and any(c.isalpha() for c in name)])
        
        self._create_single_widgets()
        self._create_express_widgets()
        
        # --- Общие кнопки и метки ---
        status_frame = ttk.Frame(root, padding="10"); status_frame.pack(pady=10, padx=10, fill="x")
        self.match_count_list_label = ttk.Label(status_frame, text="Добавлено постов в список: 0"); self.match_count_list_label.pack(side=tk.LEFT)
        action_buttons_frame = ttk.Frame(root, padding="10"); action_buttons_frame.pack(pady=10, padx=10, fill="x")
        self.main_add_button = ttk.Button(action_buttons_frame, text="Добавить 'Одиночный прогноз' в список", command=self.add_current_post_to_list); self.main_add_button.pack(side=tk.LEFT, padx=5, expand=True, fill="x")
        generate_all_button = ttk.Button(action_buttons_frame, text="Создать все изображения", command=self.start_generation_process); generate_all_button.pack(side=tk.LEFT, padx=5, expand=True, fill="x")
        
        self.on_post_type_change_ui() # Инициализация

    def _create_single_widgets(self):
        # ... (код создания виджетов для одиночного поста)
        single_fields_config = [("Название команды 1", "team1_name"), ("Название команды 2", "team2_name")]
        for i, (label_text, key) in enumerate(single_fields_config):
            label = ttk.Label(self.single_post_frame, text=label_text + ":"); label.grid(row=i, column=0, padx=5, pady=6, sticky="w")
            widget = ttk.Combobox(self.single_post_frame, width=35, values=self.team_names_for_combobox, state="normal")
            widget.bind('<KeyRelease>', lambda ev, e=widget, o=self.team_names_for_combobox: self.update_combobox_filter(e,o))
            logo_preview = ttk.Label(self.single_post_frame, width=5); logo_preview.grid(row=i, column=2, padx=5)
            widget.bind("<FocusOut>", lambda ev, e=widget, lbl=logo_preview: self.update_logo_preview(e, lbl))
            widget.bind("<<ComboboxSelected>>", lambda ev, e=widget, lbl=logo_preview: self.update_logo_preview(e, lbl))
            widget.grid(row=i, column=1, padx=5, pady=6, sticky="ew"); self.single_entries[key] = widget
        other_single_fields = [("Текст VS", "vs_text"), ("Коэффициент", "coefficient"), ("Прогноз", "prediction"), ("Дата", "date_single"), ("Фон", "background_path_single")]
        for i, (label_text, key) in enumerate(other_single_fields, start=len(single_fields_config)):
            label = ttk.Label(self.single_post_frame, text=label_text + ":"); label.grid(row=i, column=0, padx=5, pady=6, sticky="w")
            if key == "background_path_single":
                widget = ttk.Entry(self.single_post_frame, width=38); browse_btn = ttk.Button(self.single_post_frame, text="Обзор...", command=lambda e=widget: self.select_background_file_action(e)); browse_btn.grid(row=i, column=2, padx=(0,5), pady=6, sticky="w")
            else: widget = ttk.Entry(self.single_post_frame, width=38)
            widget.grid(row=i, column=1, padx=5, pady=6, sticky="ew"); self.single_entries[key] = widget
        self.single_entries["vs_text"].insert(0, "VS"); self.single_entries["date_single"].insert(0, datetime.date.today().strftime("%d.%m.%Y"))
        example_button_single = ttk.Button(self.single_post_frame, text="Заполнить пример", command=self.fill_with_single_example); example_button_single.grid(row=len(single_fields_config)+len(other_single_fields), column=0, columnspan=2, pady=10)

    def _create_express_widgets(self):
        # ... (код создания виджетов для экспресса)
        express_general_fields_config = [("Заголовок экспресса", "express_title"), ("Общий коэффициент", "total_coefficient"), ("Дата экспресса", "date_express"), ("Фон для экспресса", "background_path_express")]
        for i, (label_text, key) in enumerate(express_general_fields_config):
            label = ttk.Label(self.express_post_frame, text=label_text + ":"); label.grid(row=i, column=0, padx=5, pady=6, sticky="w")
            if key == "background_path_express":
                widget = ttk.Entry(self.express_post_frame, width=38); browse_btn = ttk.Button(self.express_post_frame, text="Обзор...", command=lambda e=widget: self.select_background_file_action(e)); browse_btn.grid(row=i, column=2, padx=(0,5), pady=6, sticky="w")
            else: widget = ttk.Entry(self.express_post_frame, width=38)
            widget.grid(row=i, column=1, padx=5, pady=6, sticky="ew"); self.express_general_entries[key] = widget
        self.express_general_entries["date_express"].insert(0, datetime.date.today().strftime("%d.%m.%Y"))
        leg_frame = ttk.LabelFrame(self.express_post_frame, text="Добавить событие", padding="10"); leg_frame.grid(row=len(express_general_fields_config), column=0, columnspan=3, pady=10, sticky="ew")
        leg_fields_config = [("Команда 1", "leg_team1_name"), ("Команда 2", "leg_team2_name"), ("Ставка", "leg_bet_text"), ("Коэфф.", "leg_coefficient")]
        for i, (label_text, key) in enumerate(leg_fields_config):
            label = ttk.Label(leg_frame, text=label_text + ":"); label.grid(row=i, column=0, padx=5, pady=4, sticky="w")
            if "team" in key:
                widget = ttk.Combobox(leg_frame, width=30, values=self.team_names_for_combobox, state="normal")
                widget.bind('<KeyRelease>', lambda ev, e=widget, o=self.team_names_for_combobox: self.update_combobox_filter(e,o))
                logo_preview = ttk.Label(leg_frame, width=5); logo_preview.grid(row=i, column=2, padx=5)
                widget.bind("<FocusOut>", lambda ev, e=widget, lbl=logo_preview: self.update_logo_preview(e, lbl))
                widget.bind("<<ComboboxSelected>>", lambda ev, e=widget, lbl=logo_preview: self.update_logo_preview(e, lbl))
            else: widget = ttk.Entry(leg_frame, width=33)
            widget.grid(row=i, column=1, padx=5, pady=4, sticky="ew"); self.express_leg_entries[key] = widget
        add_leg_button = ttk.Button(leg_frame, text="➕ Добавить событие", command=self.add_leg_to_ui_buffer); add_leg_button.grid(row=len(leg_fields_config), column=0, columnspan=2, pady=10)
        legs_display_frame = ttk.LabelFrame(self.express_post_frame, text=f"События (макс. {MAX_LEGS_IN_EXPRESS})", padding="10"); legs_display_frame.grid(row=len(express_general_fields_config)+1, column=0, columnspan=3, pady=10, sticky="ew")
        columns = ("#", "team1", "team2", "bet", "coeff"); self.legs_treeview = ttk.Treeview(legs_display_frame, columns=columns, show="headings", height=5)
        for col, width in [("#", 30), ("team1", 120), ("team2", 120), ("bet", 150), ("coeff", 70)]: self.legs_treeview.heading(col, text=col.replace("1"," 1").replace("2"," 2").capitalize()); self.legs_treeview.column(col, width=width, anchor='center' if col in ["#", "coeff"] else 'w')
        self.legs_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scrollbar = ttk.Scrollbar(legs_display_frame, orient="vertical", command=self.legs_treeview.yview); scrollbar.pack(side=tk.RIGHT, fill="y"); self.legs_treeview.configure(yscrollcommand=scrollbar.set)
        remove_leg_button = ttk.Button(self.express_post_frame, text="➖ Удалить выбранное", command=self.remove_selected_leg_from_ui_buffer); remove_leg_button.grid(row=len(express_general_fields_config)+2, column=0, columnspan=3, pady=5)
        example_button_express = ttk.Button(self.express_general_entries["express_title"].master, text="Заполнить пример", command=self.fill_with_express_example); example_button_express.grid(row=len(express_general_fields_config), column=0, columnspan=2, pady=20)

    # ... (все остальные функции GUI, такие как on_post_type_change_ui, add_leg_to_ui_buffer и т.д., теперь методы этого класса)
    def on_post_type_change_ui(self, event=None):
        global current_express_legs_buffer
        current_express_legs_buffer = []
        self.update_legs_treeview()
        selected_type = self.post_type_var.get()
        if selected_type == "Одиночный прогноз":
            self.single_post_frame.pack(fill="both", expand=True)
            self.express_post_frame.pack_forget()
            self.main_add_button.config(text="Добавить 'Одиночный прогноз' в список")
        else:
            self.single_post_frame.pack_forget()
            self.express_post_frame.pack(fill="both", expand=True)
            self.main_add_button.config(text="Добавить 'Экспресс' в список")

    def add_current_post_to_list(self):
        # ...
        global match_data_list
        post_type = self.post_type_var.get()
        final_post_data = {"post_type": post_type}

        if post_type == "Одиночный прогноз":
            # ...
            team1_name = self.single_entries["team1_name"].get().strip(); team2_name = self.single_entries["team2_name"].get().strip()
            if not (team1_name and team2_name): messagebox.showerror("Ошибка", "Укажите обе команды!"); return
            team1_logo_ref = self.get_logo_ref_for_team(team1_name); team2_logo_ref = self.get_logo_ref_for_team(team2_name)
            final_post_data.update({"team1": {"name": team1_name, "logo_ref": team1_logo_ref}, "team2": {"name": team2_name, "logo_ref": team2_logo_ref}, "vs_text": self.single_entries["vs_text"].get() or "VS", "coefficient": self.single_entries["coefficient"].get(), "prediction": self.single_entries["prediction"].get(), "date": self.single_entries["date_single"].get() or datetime.date.today().strftime("%d.%m.%Y"), "background_path": self.single_entries["background_path_single"].get().strip()})
            for key in ["team1_name", "team2_name", "coefficient", "prediction"]:
                if key in self.single_entries: self.single_entries[key].delete(0, tk.END)
            self.single_entries["team1_name"].focus()
        else: # Экспресс
            # ...
            if not current_express_legs_buffer: messagebox.showerror("Ошибка", "Добавьте событие!"); return
            total_coeff_str = self.express_general_entries["total_coefficient"].get().strip()
            if not total_coeff_str: messagebox.showerror("Ошибка", "Укажите общий коэфф.!"); return
            try: float(total_coeff_str.replace(',','.'))
            except ValueError: messagebox.showerror("Ошибка", "Общий коэфф. должен быть числом!"); return
            final_post_data.update({"express_title": self.express_general_entries["express_title"].get().strip(), "total_coefficient": total_coeff_str, "date": self.express_general_entries["date_express"].get() or datetime.date.today().strftime("%d.%m.%Y"), "legs": list(current_express_legs_buffer), "background_path": self.express_general_entries["background_path_express"].get().strip()})
            current_express_legs_buffer.clear(); self.update_legs_treeview()
            for key in ["express_title", "total_coefficient"]:
                if key in self.express_general_entries: self.express_general_entries[key].delete(0, tk.END)
            self.express_leg_entries["leg_team1_name"].focus()
            
        match_data_list.append(final_post_data)
        self.match_count_list_label.config(text=f"Добавлено постов в список: {len(match_data_list)}")

    def start_generation_process(self):
        # Эта функция будет вызывать callback из main.py
        self.on_generate_callback(match_data_list, self.root)

    def run(self, on_generate_callback):
        self.on_generate_callback = on_generate_callback
        self.generate_all_button = ttk.Button(
            self.root.nametowidget('.!frame3'), # Получаем доступ к action_buttons_frame
            text="Создать все изображения из списка", 
            command=self.start_generation_process
        )
        self.generate_all_button.pack(side=tk.LEFT, padx=10, expand=True, fill="x")
        self.root.mainloop()


# --- Точка входа ---
if __name__ == '__main__':
    if not os.path.exists(LOGO_DIR):
        try: os.makedirs(LOGO_DIR)
        except OSError as e: messagebox.showerror("Ошибка папки", f"Не удалось создать папку: {LOGO_DIR}\n{e}")
    
    # Это будет заглушкой, если gui.py запускается напрямую
    def dummy_generator(data, root):
        messagebox.showinfo("Запуск", f"Запущена генерация для {len(data)} постов (заглушка).")
        print(data)
        root.destroy()
        
    app = MatchGeneratorGUI()
    app.run(on_generate_callback=dummy_generator)