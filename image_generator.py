# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os
from config import FONT_PATH, IMAGE_SIZE, DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2, IMAGE_QUALITY

# --- Вспомогательные функции отрисовки ---

def get_font_for_cell(draw_context, text_to_fit, target_width, target_height, initial_font_size=40, min_font_size=10, max_lines=3, line_spacing_ratio=1.2):
    """
    Подбирает оптимальный шрифт, чтобы текст поместился в заданные рамки.
    Эта версия исправляет ошибку UnboundLocalError.
    """
    # **ИСПРАВЛЕНИЕ:** Переменная 'current_font_size' инициализируется здесь, до начала цикла.
    # Это гарантирует, что она всегда имеет значение.
    current_font_size = initial_font_size
    best_font = None
    best_lines = [text_to_fit]

    if not text_to_fit or not text_to_fit.strip():
        try:
            return ImageFont.truetype(FONT_PATH, min_font_size), [""]
        except IOError:
            return ImageFont.load_default(), [""]

    while current_font_size >= min_font_size:
        try:
            current_font = ImageFont.truetype(FONT_PATH, current_font_size)
        except IOError:
            if current_font_size == min_font_size:
                return ImageFont.load_default(), best_lines
            current_font_size -= 1
            continue

        words = text_to_fit.split()
        lines = []
        current_line_text = ""

        for word in words:
            test_line = current_line_text + (" " if current_line_text else "") + word
            try:
                line_width = draw_context.textlength(test_line, font=current_font)
            except AttributeError:
                bbox_fallback = draw_context.textbbox((0,0), test_line, font=current_font)
                line_width = bbox_fallback[2] - bbox_fallback[0]

            if line_width <= target_width:
                current_line_text = test_line
            else:
                if current_line_text:
                    lines.append(current_line_text)
                current_line_text = word
        
        if current_line_text:
            lines.append(current_line_text)
        if not lines and text_to_fit:
            lines = [text_to_fit]

        actual_total_height = 0
        if lines:
            spacing_val = int(current_font_size * (line_spacing_ratio - 1.0))
            block_bbox = draw_context.multiline_textbbox((0,0), "\n".join(lines), font=current_font, spacing=spacing_val)
            actual_total_height = block_bbox[3] - block_bbox[1]

        if len(lines) <= max_lines and actual_total_height <= target_height:
            return current_font, lines

        if current_font_size == min_font_size:
            best_font = current_font
            best_lines = lines
            if len(lines) > max_lines or actual_total_height > target_height:
                 print(f"Предупреждение: Текст '{text_to_fit[:30]}...' не вписался идеально.")
            break

        current_font_size -= 1
        best_font = current_font
        best_lines = lines

    return best_font or ImageFont.load_default(), best_lines


def draw_text_with_effects(draw, text_block, center_xy, font, color, shadow_color, stroke_color, is_multiline=False):
    x, y = center_xy
    align = "center" if is_multiline else "left"
    spacing = int(font.size * 0.2)
    
    if is_multiline:
        bbox = draw.multiline_textbbox((0,0), text_block, font=font, spacing=spacing, align=align)
    else:
        bbox = draw.textbbox((0,0), text_block, font=font)
    
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pos = (x - text_w / 2, y - text_h / 2)
    
    if shadow_color:
        if is_multiline:
            draw.multiline_text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color, spacing=spacing, align=align)
        else:
            draw.text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color)
    
    if is_multiline:
        draw.multiline_text(pos, text_block, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color, spacing=spacing, align=align)
    else:
        draw.text(pos, text_block, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color)

def create_gradient_bg(width, height, color1, color2):
    image = Image.new('RGB', (width, height)); draw = ImageDraw.Draw(image)
    r1,g1,b1=color1; r2,g2,b2=color2
    for i in range(height):
        r = int(r1 + (r2-r1)*i/height); g = int(g1 + (g2-g1)*i/height); b = int(b1 + (b2-b1)*i/height)
        draw.line([(0,i), (width,i)], fill=(r,g,b))
    return image

# --- Генератор для одиночного поста ---
def create_single_image(match_content, background_path, output_filename):
    image = None
    if background_path and os.path.exists(background_path):
        try:
            image = Image.open(background_path).convert("RGB").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        except Exception as e: print(f"Ошибка фона: {e}")
    if image is None:
        image = create_gradient_bg(IMAGE_SIZE[0], IMAGE_SIZE[1], DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2)
    
    draw = ImageDraw.Draw(image); padding = 15
    user_defined_cells = [
        {'type': 'team_name',   'x': 350, 'y': 200, 'w': 250, 'h': 70},
        {'type': 'team_name',   'x': 950, 'y': 200, 'w': 250, 'h': 70},
        {'type': 'logo',        'x': 350, 'y': 350, 'w': 200, 'h': 220},
        {'type': 'logo',        'x': 950, 'y': 350, 'w': 200, 'h': 220},
        {'type': 'vs_text',     'x': 650, 'y': 350, 'w': 100, 'h': 100},
        {'type': 'coefficient', 'x': 650, 'y': 550, 'w': 150, 'h': 150},
        {'type': 'prediction',  'x': 650, 'y': 870, 'w': 900, 'h': 300},
        {'type': 'date',        'x': 650, 'y': 1150,'w': 200, 'h': 40}, # Увеличил размеры для даты для лучшей читаемости
    ]
    content_map = [match_content["team1"]["name"], match_content["team2"]["name"], match_content["team1"]["logo"], match_content["team2"]["logo"], match_content["vs_text"], match_content["coefficient"], match_content["prediction"], match_content["date"]]
    
    for idx, cell in enumerate(user_defined_cells):
        content = str(content_map[idx]); is_multiline = False
        font_params = {}; text_color = '#FFFFFF'; shadow = '#444444'; outline = '#000000'

        if cell['type'] == 'team_name': font_params = {'initial_font_size': 50, 'min_font_size': 18, 'max_lines': 3}; text_color = '#E0E0E0'
        elif cell['type'] == 'vs_text': font_params = {'initial_font_size': 60, 'min_font_size': 30, 'max_lines': 1}; text_color = '#FFD700'
        elif cell['type'] == 'coefficient': font_params = {'initial_font_size': 70, 'min_font_size': 30, 'max_lines': 1}; text_color = '#4CAF50'
        elif cell['type'] == 'prediction': font_params = {'initial_font_size': 45, 'min_font_size': 16, 'max_lines': 7}; text_color = '#FFFFFF'; is_multiline = True
        elif cell['type'] == 'date': font_params = {'initial_font_size': 25, 'min_font_size': 10, 'max_lines': 1}; text_color = '#AAAAAA'
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
    
    try:
        image.save(output_filename, quality=IMAGE_QUALITY)
        print(f"Создано изображение: {output_filename}")
    except Exception as e:
        print(f"Ошибка сохранения {output_filename}: {e}")

# --- Генератор для экспресс-поста ---
def create_express_image(express_content, background_path, output_filename):
    image = None
    if background_path and os.path.exists(background_path):
        try:
            image = Image.open(background_path).convert("RGB").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        except Exception as e: print(f"Ошибка фона: {e}")
    if image is None:
        image = create_gradient_bg(IMAGE_SIZE[0], IMAGE_SIZE[1], DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2)
    
    draw = ImageDraw.Draw(image)
    padding = 40
    
    # ... (код отрисовки экспресса остается как в предыдущем ответе) ...
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
            teams_text = f"{leg['team1_name']} - {leg['team2_name']}"; teams_text_width_target = col_match_width - 2*logo_w - 4*padding
            font_teams, lines_teams = get_font_for_cell(draw, teams_text, teams_text_width_target, row_height*0.8, initial_font_size=30, min_font_size=12, max_lines=2)
            draw_text_with_effects(draw, "\n".join(lines_teams), (col_match_x_start + col_match_width/2, row_y_center), font_teams, '#FFFFFF', '#000000', '#000000', is_multiline=len(lines_teams)>1)
            col_bet_width = table_width * col_widths_percent['bet']; col_bet_x_center = col_match_x_start + col_match_width + col_bet_width/2
            bet_text = leg['bet_text']; font_bet, lines_bet = get_font_for_cell(draw, bet_text, col_bet_width - padding, row_height*0.8, initial_font_size=28, min_font_size=12, max_lines=3)
            draw_text_with_effects(draw, "\n".join(lines_bet), (col_bet_x_center, row_y_center), font_bet, '#E0E0E0', '#000000', '#000000', is_multiline=len(lines_bet)>1)
            col_coeff_width = table_width * col_widths_percent['coeff']; col_coeff_x_center = col_match_x_start + col_match_width + col_bet_width + col_coeff_width/2
            coeff_text = leg['leg_coefficient']; font_coeff, _ = get_font_for_cell(draw, coeff_text, col_coeff_width - padding, row_height*0.8, initial_font_size=35, min_font_size=16, max_lines=1)
            draw_text_with_effects(draw, coeff_text, (col_coeff_x_center, row_y_center), font_coeff, '#4CAF50', '#000000', '#000000')
    footer_y_pos = table_bottom_y + (IMAGE_SIZE[1] - table_bottom_y) / 2
    total_coeff_text = f"Общий коэффициент: {express_content['total_coefficient']}"; font_total_coeff, _ = get_font_for_cell(draw, total_coeff_text, table_width, 100, initial_font_size=50, min_font_size=25, max_lines=1)
    draw_text_with_effects(draw, total_coeff_text, (IMAGE_SIZE[0]/2, footer_y_pos), font_total_coeff, '#FFD700', '#000000', '#000000')
    try:
        image.save(output_filename, quality=IMAGE_QUALITY)
        print(f"Создано изображение (экспресс): {output_filename}")
    except Exception as e: print(f"Ошибка сохранения {output_filename}: {e}")