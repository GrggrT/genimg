# image_generator.py (ФИНАЛЬНАЯ ВЕРСИЯ С ИСПРАВЛЕННЫМ ДИЗАЙНОМ)
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import IMAGE_SIZE, DEFAULT_BACKGROUND_COLOR_1, DEFAULT_BACKGROUND_COLOR_2, IMAGE_QUALITY, FONT_PATH

def open_image_safely(path, default_size=(100, 100)):
    """Безопасно открывает изображение, возвращая плейсхолдер при ошибке."""
    if path and os.path.exists(path):
        try:
            return Image.open(path).convert("RGBA")
        except Exception as e:
            print(f"Ошибка при открытии изображения {path}: {e}")
    return Image.new("RGBA", default_size, (200, 200, 200, 50)) # Полупрозрачный серый квадрат

def draw_single_match_post(post_data, output_folder, filename):
    """Генерирует изображение для одиночного прогноза."""
    try:
        # --- ФОН ---
        if post_data.get("background_path") and os.path.exists(post_data["background_path"]):
            base_img = Image.open(post_data["background_path"]).convert("RGBA").resize(IMAGE_SIZE)
        else:
            base_img = Image.new("RGB", IMAGE_SIZE, DEFAULT_BACKGROUND_COLOR_1)
        
        draw = ImageDraw.Draw(base_img)
        font_path = FONT_PATH
        
        # --- ЛОГОТИПЫ И НАЗВАНИЯ КОМАНД ---
        team1_logo = open_image_safely(post_data["team1"]["logo_ref"]).resize((200, 200), Image.Resampling.LANCZOS)
        team2_logo = open_image_safely(post_data["team2"]["logo_ref"]).resize((200, 200), Image.Resampling.LANCZOS)
        
        base_img.paste(team1_logo, (300, 250), team1_logo)
        base_img.paste(team2_logo, (780, 250), team2_logo)

        font_teams = ImageFont.truetype(font_path, 60)
        draw.text((IMAGE_SIZE[0]/2, 500), post_data["team1"]["name"], font=font_teams, fill="white", anchor="ms")
        draw.text((IMAGE_SIZE[0]/2, 560), post_data["team2"]["name"], font=font_teams, fill="white", anchor="ms")

        # --- ТЕКСТ "VS" ---
        font_vs = ImageFont.truetype(font_path, 80)
        draw.text((IMAGE_SIZE[0]/2, 350), post_data.get("vs_text", "VS"), font=font_vs, fill="yellow", anchor="mm")

        # --- ПРОГНОЗ И КОЭФФИЦИЕНТ ---
        prediction_text = post_data.get("prediction", "")
        coefficient_text = post_data.get("coefficient", "")
        
        font_prediction = ImageFont.truetype(font_path, 55)
        font_coefficient = ImageFont.truetype(font_path, 70)
        
        draw.text((IMAGE_SIZE[0]/2, 750), prediction_text, font=font_prediction, fill="white", anchor="ms")
        draw.text((IMAGE_SIZE[0]/2, 850), coefficient_text, font=font_coefficient, fill="yellow", anchor="ms")
        
        # --- ДАТА ---
        # ИЗМЕНЕНИЕ: Размер шрифта даты теперь 35, как в экспрессе
        font_date = ImageFont.truetype(font_path, 35)
        draw.text((IMAGE_SIZE[0]/2, 1000), post_data.get("date", ""), font=font_date, fill="white", anchor="ms")

        # --- СОХРАНЕНИЕ ---
        output_path = os.path.join(output_folder, filename)
        base_img.convert("RGB").save(output_path, quality=IMAGE_QUALITY)
        return True, output_path

    except Exception as e:
        print(f"Критическая ошибка при создании одиночного поста: {e}")
        return False, str(e)


def draw_express_post(post_data, output_folder, filename):
    """Генерирует изображение для экспресса с новой версткой."""
    try:
        # --- ФОН ---
        if post_data.get("background_path") and os.path.exists(post_data["background_path"]):
            base_img = Image.open(post_data["background_path"]).convert("RGBA").resize(IMAGE_SIZE)
        else:
            base_img = Image.new("RGB", IMAGE_SIZE, DEFAULT_BACKGROUND_COLOR_1)

        draw = ImageDraw.Draw(base_img)
        font_path = FONT_PATH
        
        # --- ЗАГОЛОВОК И ДАТА ---
        y_cursor = 100
        express_title = post_data.get("express_title", "ЭКСПРЕСС")
        font_title = ImageFont.truetype(font_path, 70)
        draw.text((IMAGE_SIZE[0]/2, y_cursor), express_title, font=font_title, fill="yellow", anchor="ms")
        y_cursor += 80

        date_text = post_data.get("date", "")
        font_date = ImageFont.truetype(font_path, 35)
        draw.text((IMAGE_SIZE[0]/2, y_cursor), date_text, font=font_date, fill="white", anchor="ms")
        y_cursor += 100

        # --- ШРИФТЫ ДЛЯ СОБЫТИЙ ---
        font_team_name = ImageFont.truetype(font_path, 38)
        font_vs_small = ImageFont.truetype(font_path, 25) # Маленький шрифт для "VS"
        font_bet_text = ImageFont.truetype(font_path, 40)
        
        # --- ОТРИСОВКА СОБЫТИЙ (ЛЕГОВ) ---
        logo_size = (100, 100)
        padding_between_elements = 20 # Отступ между лого и текстом
        
        for leg in post_data["legs"]:
            # --- НОВАЯ ЛОГИКА ВЕРСТКИ ---
            team1_logo = open_image_safely(leg["team1_logo_ref"]).resize(logo_size, Image.Resampling.LANCZOS)
            team2_logo = open_image_safely(leg["team2_logo_ref"]).resize(logo_size, Image.Resampling.LANCZOS)
            
            # --- РАСЧЕТ РАЗМЕРОВ БЛОКА С НАЗВАНИЯМИ ---
            t1_box = draw.textbbox((0,0), leg["team1_name"], font=font_team_name)
            vs_box = draw.textbbox((0,0), "VS", font=font_vs_small)
            t2_box = draw.textbbox((0,0), leg["team2_name"], font=font_team_name)

            text_block_width = max(t1_box[2], vs_box[2], t2_box[2]) # Ширина блока равна самому длинному тексту
            text_block_height = logo_size[1] # Высота текстового блока для простоты равна высоте лого

            # --- РАСЧЕТ ОБЩЕЙ ШИРИНЫ И НАЧАЛЬНОЙ ТОЧКИ ДЛЯ ЦЕНТРИРОВАНИЯ ---
            total_block_width = logo_size[0] + padding_between_elements + text_block_width + padding_between_elements + logo_size[0]
            start_x = (IMAGE_SIZE[0] - total_block_width) / 2
            
            # --- ОТРИСОВКА ЭЛЕМЕНТОВ ---
            # 1. Логотип команды 1
            x_cursor = start_x
            base_img.paste(team1_logo, (int(x_cursor), int(y_cursor)), team1_logo)
            x_cursor += logo_size[0] + padding_between_elements

            # 2. Блок с текстом (Команда1, VS, Команда2)
            # Вертикальное выравнивание текста по центру относительно логотипа
            text_y_start = y_cursor + (logo_size[1] - (t1_box[3] + vs_box[3] + t2_box[3])) / 2
            
            draw.text((x_cursor, text_y_start), leg["team1_name"], font=font_team_name, fill="white", anchor="lt")
            draw.text((x_cursor + text_block_width / 2, text_y_start + t1_box[3] + 5), "VS", font=font_vs_small, fill="yellow", anchor="mt")
            draw.text((x_cursor, text_y_start + t1_box[3] + vs_box[3] + 10), leg["team2_name"], font=font_team_name, fill="white", anchor="lt")
            x_cursor += text_block_width + padding_between_elements

            # 3. Логотип команды 2
            base_img.paste(team2_logo, (int(x_cursor), int(y_cursor)), team2_logo)
            
            # --- СТАВКА ---
            y_cursor += logo_size[1] + 15 # Перемещаем курсор вниз под логотипы
            draw.text((IMAGE_SIZE[0]/2, y_cursor), leg["bet_text"], font=font_bet_text, fill="white", anchor="ms")
            y_cursor += 70 # Отступ между событиями
        
        # --- ОБЩИЙ КОЭФФИЦИЕНТ ---
        y_cursor = max(y_cursor, IMAGE_SIZE[1] - 150) # Убедимся, что коэфф. не уедет за экран
        font_total_coeff = ImageFont.truetype(font_path, 80)
        draw.text((IMAGE_SIZE[0]/2, y_cursor), post_data["total_coefficient"], font=font_total_coeff, fill="yellow", anchor="ms")
        
        # --- СОХРАНЕНИЕ ---
        output_path = os.path.join(output_folder, filename)
        base_img.convert("RGB").save(output_path, quality=IMAGE_QUALITY)
        return True, output_path

    except Exception as e:
        print(f"Критическая ошибка при создании экспресса: {e}")
        return False, str(e)