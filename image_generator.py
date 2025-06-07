# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os
from config import FONT_PATH, LOGO_DIR

# --- Вспомогательные функции отрисовки ---
def get_font_for_cell(draw_context, text_to_fit, target_width, target_height, initial_font_size=40, min_font_size=10, max_lines=3):
    font_size = initial_font_size
    while font_size >= min_font_size:
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except IOError:
            return ImageFont.load_default(), [text_to_fit]
        words = text_to_fit.split(); lines = []; current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            line_width = draw_context.textlength(test_line, font=font)
            if line_width <= target_width:
                current_line = test_line
            else:
                if current_line: lines.append(current_line)
                current_line = word
        if current_line: lines.append(current_line)
        if not lines and text_to_fit: lines = [text_to_fit]
        
        block_bbox = draw_context.multiline_textbbox((0,0), "\n".join(lines), font=font, spacing=int(font_size*0.2))
        total_height = block_bbox[3] - block_bbox[1]
        
        if len(lines) <= max_lines and total_height <= target_height:
            return font, lines
        font_size -= 1
    
    final_font = ImageFont.truetype(FONT_PATH, min_font_size)
    print(f"Предупреждение: Текст '{text_to_fit[:30]}...' не вписался идеально.")
    return final_font, lines

def draw_text_with_effects(draw, text_block, center_xy, font, color, shadow_color, stroke_color, is_multiline=False):
    x, y = center_xy
    align = "center" if is_multiline else "left"
    spacing = int(font.size * 0.2) if is_multiline else 0
    
    try:
        if is_multiline:
            bbox = draw.multiline_textbbox((0,0), text_block, font=font, spacing=spacing, align=align)
        else:
            bbox = draw.textbbox((0,0), text_block, font=font)
    except AttributeError: # Фоллбэк для старых Pillow
        bbox = (0,0,100,20) # Примерный bbox

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pos = (x - text_w / 2, y - text_h / 2)
    
    # Тень
    if shadow_color:
        if is_multiline:
            draw.multiline_text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color, spacing=spacing, align=align)
        else:
            draw.text((pos[0] + 2, pos[1] + 2), text_block, font=font, fill=shadow_color)
    
    # Основной текст с контуром
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
    image = None; image_size = (1280, 1280)
    if background_path and os.path.exists(background_path):
        try:
            image = Image.open(background_path).convert("RGB").resize(image_size, Image.Resampling.LANCZOS)
        except Exception as e: print(f"Ошибка фона: {e}")
    if image is None:
        image = create_gradient_bg(image_size[0], image_size[1], (28, 37, 38), (0, 0, 0))
    
    draw = ImageDraw.Draw(image); padding = 15
    user_defined_cells = [
        {'type': 'team_name',   'x': 350, 'y': 200, 'w': 250, 'h': 70}, # 0
        {'type': 'team_name',   'x': 950, 'y': 200, 'w': 250, 'h': 70}, # 1
        {'type': 'logo',        'x': 350, 'y': 350, 'w': 200, 'h': 220}, # 2
        {'type': 'logo',        'x': 950, 'y': 350, 'w': 200, 'h': 220}, # 3
        {'type': 'vs_text',     'x': 650, 'y': 350, 'w': 100, 'h': 100}, # 4
        {'type': 'coefficient', 'x': 650, 'y': 550, 'w': 150, 'h': 150}, # 5
        {'type': 'prediction',  'x': 650, 'y': 870, 'w': 900, 'h': 300}, # 6
        {'type': 'date',        'x': 650, 'y': 1150,'w': 100, 'h': 30}, # 7
    ]
    
    content_map = [
        match_content["team1"]["name"], match_content["team2"]["name"],
        match_content["team1"]["logo"], match_content["team2"]["logo"],
        match_content["vs_text"], match_content["coefficient"],
        match_content["prediction"], match_content["date"]
    ]
    
    for idx, cell in enumerate(user_defined_cells):
        content = str(content_map[idx])
        is_multiline = False
        font_params = {}
        text_color = '#FFFFFF'; shadow = '#444444'; outline = '#000000'

        if cell['type'] == 'team_name': font_params = {'initial_font_size': 50, 'min_font_size': 18, 'max_lines': 3}; text_color = '#E0E0E0'
        elif cell['type'] == 'vs_text': font_params = {'initial_font_size': 60, 'min_font_size': 30, 'max_lines': 1}; text_color = '#FFD700'
        elif cell['type'] == 'coefficient': font_params = {'initial_font_size': 70, 'min_font_size': 30, 'max_lines': 1}; text_color = '#4CAF50'
        elif cell['type'] == 'prediction': font_params = {'initial_font_size': 45, 'min_font_size': 16, 'max_lines': 7}; text_color = '#FFFFFF'; is_multiline = True
        elif cell['type'] == 'date': font_params = {'initial_font_size': 30, 'min_font_size': 10, 'max_lines': 1}; text_color = '#AAAAAA'
        elif cell['type'] == 'logo':
            logo_path = content
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path).convert("RGBA")
                    logo_img.thumbnail((cell['w'], cell['h']), Image.Resampling.LANCZOS)
                    pos_x = cell['x'] - logo_img.width // 2; pos_y = cell['y'] - logo_img.height // 2
                    shadow_pos = (pos_x + 3, pos_y + 3)
                    image.paste((50,50,50), [shadow_pos[0], shadow_pos[1], shadow_pos[0]+logo_img.width, shadow_pos[1]+logo_img.height])
                    image.paste(logo_img, (pos_x, pos_y), logo_img)
                except Exception as e: print(f"Ошибка отрисовки лого '{logo_path}': {e}")
            else: # Плейсхолдер
                team_name_placeholder = content_map[0] if idx == 2 else content_map[1]
                draw.rectangle((cell['x']-cell['w']//2, cell['y']-cell['h']//2, cell['x']+cell['w']//2, cell['y']+cell['h']//2), fill=(70,70,70))
                font_obj, lines = get_font_for_cell(draw, team_name_placeholder, cell['w']-2*padding, cell['h']-2*padding, initial_font_size=30, max_lines=3)
                draw_text_with_effects(draw, "\n".join(lines), (cell['x'], cell['y']), font_obj, '#DDDDDD', shadow, outline, is_multiline=True)
            continue
        
        font, lines = get_font_for_cell(draw, content, cell['w']-2*padding, cell['h']-2*padding, **font_params)
        draw_text_with_effects(draw, "\n".join(lines), (cell['x'], cell['y']), font, text_color, shadow, outline, is_multiline=is_multiline or len(lines)>1)
    
    try: image.save(output_filename, quality=IMAGE_QUALITY); print(f"Создано изображение: {output_filename}")
    except Exception as e: print(f"Ошибка сохранения {output_filename}: {e}")

# --- Генератор для экспресс-поста (ЗАГЛУШКА) ---
def create_express_image(express_content, background_path, output_filename):
    print(f"ЗАГЛУШКА: Вызов create_express_image для: {output_filename}")
    temp_img = Image.new("RGB", (1280,1280), "darkblue")
    draw = ImageDraw.Draw(temp_img)
    try: font = ImageFont.truetype(FONT_PATH, 50)
    except IOError: font = ImageFont.load_default()
    title = express_content.get("express_title", "Экспресс")
    num_legs = len(express_content.get("legs", []))
    lang = output_filename.split('_')[-1].split('.')[0].upper()
    draw.text((100,100), f"{title}\nЯзык: {lang}\nСобытий: {num_legs}", font=font, fill="white")
    temp_img.save(output_filename)