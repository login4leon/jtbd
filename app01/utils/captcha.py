from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, string, os
from io import BytesIO

def random_string(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def text_size(draw, text, font):
    """
    Pillow 10 兼容：返回 (width, height)
    """
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top

def generate_captcha(size=(180, 60), char_length=4):
    code = random_string(char_length)
    img = Image.new('RGB', size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 1. 干扰线
    for _ in range(5):
        draw.line([(random.randint(0, size[0]), random.randint(0, size[1])),
                   (random.randint(0, size[0]), random.randint(0, size[1]))],
                  fill=(random.randint(0, 255), 0, random.randint(0, 255)), width=1)

    # 2. 字体（Linux/Windows 都保底）
    try:
        # font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
        # if not os.path.isfile(font_path):
        #     font_path = 'ZihunSans_Regular.ttf'                                    # Windows
        font = ImageFont.truetype('ZihunSans_Regular.ttf', 36)
    except IOError:
        font = ImageFont.load_default()

    # 3. 逐个画字符
    for i, ch in enumerate(code):
        w, h = text_size(draw, ch, font)
        x = 15 + i * 40 + random.randint(-5, 5)
        y = (size[1] - h) // 2 + random.randint(-5, 5)
        draw.text((x, y), ch,
                  fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)),
                  font=font)

    # 4. 噪点
    for _ in range(300):
        draw.point((random.randint(0, size[0]), random.randint(0, size[1])),
                   fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue(), code