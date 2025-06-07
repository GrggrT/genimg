from PIL import Image, ImageDraw, ImageFont
import os
from config import (
    LOGO_DIR, FONT_PATH, DEFAULT_FONT_SIZE, MIN_FONT_SIZE,
    MAX_LINES, LINE_SPACING_RATIO
)

def get_font_for_cell(text, cell_width, cell_height, initial_font_size=DEFAULT_FONT_SIZE,
                     min_font_size=MIN_FONT_SIZE, max_lines=MAX_LINES, line_spacing_ratio=LINE_SPACING_RATIO):
    font_size = initial_font_size
    while font_size >= min_font_size:
        font = ImageFont.truetype(FONT_PATH, font_size)
        lines = text.split('\n')
        if len(lines) > max_lines:
            lines = lines[:max_lines]
        
        max_line_width = 0
        total_height = 0
        
        for line in lines:
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            max_line_width = max(max_line_width, line_width)
            total_height += line_height
        
        total_height += (len(lines) - 1) * (line_height * (line_spacing_ratio - 1))
        
        if max_line_width <= cell_width * 0.9 and total_height <= cell_height * 0.9:
            return font
        
        font_size -= 2
    
    return ImageFont.truetype(FONT_PATH, min_font_size)

def draw_text_with_effects(draw_context, text, position_center, font_object, text_color, shadow_color, outline_color, stroke_thickness=1):
    x, y = position_center
    bbox = font_object.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw shadow
    shadow_offset = 2
    draw_context.text((x - text_width/2 + shadow_offset, y - text_height/2 + shadow_offset),
                     text, font=font_object, fill=shadow_color)
    
    # Draw outline
    for dx in range(-stroke_thickness, stroke_thickness + 1):
        for dy in range(-stroke_thickness, stroke_thickness + 1):
            if dx == 0 and dy == 0:
                continue
            draw_context.text((x - text_width/2 + dx, y - text_height/2 + dy),
                            text, font=font_object, fill=outline_color)
    
    # Draw main text
    draw_context.text((x - text_width/2, y - text_height/2),
                     text, font=font_object, fill=text_color)

def draw_multiline_text_with_effects(draw_context, text_block, position_center, font_object,
                                   text_color, shadow_color, outline_color, stroke_thickness=1,
                                   line_spacing=4, text_align="center"):
    lines = text_block.split('\n')
    if not lines:
        return
    
    total_height = 0
    line_heights = []
    
    # Calculate total height and individual line heights
    for line in lines:
        bbox = font_object.getbbox(line)
        line_height = bbox[3] - bbox[0]
        line_heights.append(line_height)
        total_height += line_height
    
    total_height += (len(lines) - 1) * line_spacing
    current_y = position_center[1] - total_height / 2
    
    # Draw each line
    for i, line in enumerate(lines):
        bbox = font_object.getbbox(line)
        line_width = bbox[2] - bbox[0]
        line_height = line_heights[i]
        
        x = position_center[0]
        if text_align == "center":
            x = position_center[0] - line_width / 2
        elif text_align == "right":
            x = position_center[0] - line_width
        
        # Draw shadow
        shadow_offset = 2
        draw_context.text((x + shadow_offset, current_y + shadow_offset),
                         line, font=font_object, fill=shadow_color)
        
        # Draw outline
        for dx in range(-stroke_thickness, stroke_thickness + 1):
            for dy in range(-stroke_thickness, stroke_thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                draw_context.text((x + dx, current_y + dy),
                                line, font=font_object, fill=outline_color)
        
        # Draw main text
        draw_context.text((x, current_y), line, font=font_object, fill=text_color)
        
        current_y += line_height + line_spacing

def create_gradient(width, height, color1, color2):
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return gradient

def create_single_image_for_match_data(match_content_for_image, background_image_path=None, output_filename="output.jpg"):
    # Create base image
    width, height = 1200, 630
    if background_image_path and os.path.exists(background_image_path):
        base_image = Image.open(background_image_path).convert('RGBA')
        base_image = base_image.resize((width, height))
    else:
        base_image = create_gradient(width, height, (0, 0, 0), (50, 50, 50))
    
    draw = ImageDraw.Draw(base_image)
    
    # Load and resize team logos
    team1_logo = None
    team2_logo = None
    
    if isinstance(match_content_for_image["team1"]["logo"], str) and os.path.exists(match_content_for_image["team1"]["logo"]):
        team1_logo = Image.open(match_content_for_image["team1"]["logo"]).convert('RGBA')
        team1_logo = team1_logo.resize((200, 200))
    
    if isinstance(match_content_for_image["team2"]["logo"], str) and os.path.exists(match_content_for_image["team2"]["logo"]):
        team2_logo = Image.open(match_content_for_image["team2"]["logo"]).convert('RGBA')
        team2_logo = team2_logo.resize((200, 200))
    
    # Draw team names and logos
    team1_font = get_font_for_cell(match_content_for_image["team1"]["name"], 400, 100)
    team2_font = get_font_for_cell(match_content_for_image["team2"]["name"], 400, 100)
    
    # Draw team 1
    if team1_logo:
        base_image.paste(team1_logo, (100, 215), team1_logo)
    draw_multiline_text_with_effects(draw, match_content_for_image["team1"]["name"],
                                   (350, 315), team1_font, (255, 255, 255),
                                   (0, 0, 0), (0, 0, 0))
    
    # Draw VS
    vs_font = get_font_for_cell(match_content_for_image["vs_text"], 200, 100)
    draw_text_with_effects(draw, match_content_for_image["vs_text"],
                          (600, 315), vs_font, (255, 255, 255),
                          (0, 0, 0), (0, 0, 0))
    
    # Draw team 2
    if team2_logo:
        base_image.paste(team2_logo, (900, 215), team2_logo)
    draw_multiline_text_with_effects(draw, match_content_for_image["team2"]["name"],
                                   (850, 315), team2_font, (255, 255, 255),
                                   (0, 0, 0), (0, 0, 0))
    
    # Draw coefficient and prediction
    if match_content_for_image["coefficient"]:
        coef_font = get_font_for_cell(match_content_for_image["coefficient"], 200, 100)
        draw_text_with_effects(draw, match_content_for_image["coefficient"],
                              (600, 415), coef_font, (255, 255, 255),
                              (0, 0, 0), (0, 0, 0))
    
    if match_content_for_image["prediction"]:
        pred_font = get_font_for_cell(match_content_for_image["prediction"], 800, 100)
        draw_multiline_text_with_effects(draw, match_content_for_image["prediction"],
                                       (600, 515), pred_font, (255, 255, 255),
                                       (0, 0, 0), (0, 0, 0))
    
    # Draw date
    if match_content_for_image["date"]:
        date_font = get_font_for_cell(match_content_for_image["date"], 200, 50)
        draw_text_with_effects(draw, match_content_for_image["date"],
                              (1000, 50), date_font, (255, 255, 255),
                              (0, 0, 0), (0, 0, 0))
    
    # Save the image
    base_image.save(output_filename, quality=95)
    print(f"Создано изображение: {output_filename}") 