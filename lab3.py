try:
    from PIL import Image
except ImportError:
    print("Ошибка: установите библиотеку Pillow командой: pip install pillow")
    raise SystemExit


def read_keys(file_name):
    """Чтение координат из файла ключей."""

    keys = []

    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            line = line.replace("(", " ")
            line = line.replace(")", " ")
            line = line.replace(",", " ")
            line = line.replace(";", " ")

            parts = line.split()
            numbers = []

            for part in parts:
                if part.isdigit():
                    numbers.append(int(part))

            if len(numbers) >= 2:
                keys.append((numbers[-2], numbers[-1]))

    return keys


def decode_blue_channel(image_name, keys_name):
    """Декодирование текста из синего канала изображения."""

    image = Image.open(image_name).convert("RGB")
    keys = read_keys(keys_name)
    width, height = image.size

    byte_values = []

    for x, y in keys:
        if 0 <= x < width and 0 <= y < height:
            red, green, blue = image.getpixel((x, y))
            byte_values.append(blue)

    message_bytes = bytes(byte_values)

    try:
        message = message_bytes.decode("utf-8")
    except UnicodeDecodeError:
        message = message_bytes.decode("cp1251", errors="ignore")

    message = message.replace("\x00", "")

    print("Декодированное сообщение:")
    print(message)


def set_last_two_bits(color_value, bits):
    """Замена двух младших битов цвета."""

    return (color_value & 252) | int(bits, 2)


def encode_text(image_name, output_name, text):
    """Кодирование текста в изображение."""

    image = Image.open(image_name).convert("RGB")
    pixels = image.load()
    width, height = image.size

    text_bytes = text.encode("utf-8")
    need_pixels = len(text_bytes) * 2

    if need_pixels > width * height:
        print("Ошибка: текст слишком длинный для изображения.")
        return 0

    pixel_number = 0
    first_symbol_bits = ""
    old_pixels = []
    new_pixels = []

    for byte_number in range(len(text_bytes)):
        byte = text_bytes[byte_number]
        bits = format(byte, "08b")

        if byte_number == 0:
            first_symbol_bits = bits

        parts = [bits[:4], bits[4:]]

        for part in parts:
            x = pixel_number % width
            y = pixel_number // width

            red, green, blue = pixels[x, y]
            old_pixel = (red, green, blue)

            new_red = set_last_two_bits(red, part[:2])
            new_blue = set_last_two_bits(blue, part[2:])

            new_pixel = (new_red, green, new_blue)
            pixels[x, y] = new_pixel

            if byte_number == 0:
                old_pixels.append(old_pixel)
                new_pixels.append(new_pixel)

            pixel_number += 1

    image.save(output_name)

    print("Текст успешно закодирован.")
    print("Файл с результатом:", output_name)
    print("Биты первого символа:", first_symbol_bits)
    print("Исходные значения пикселей:", old_pixels)
    print("Изменённые значения пикселей:", new_pixels)

    return len(text_bytes)


def decode_own_image(image_name, byte_count):
    """Декодирование текста, записанного в красный и синий каналы."""

    image = Image.open(image_name).convert("RGB")
    pixels = image.load()
    width, height = image.size

    result_bytes = []
    pixel_number = 0

    for i in range(byte_count):
        bits = ""

        for j in range(2):
            if pixel_number >= width * height:
                break

            x = pixel_number % width
            y = pixel_number // width

            red, green, blue = pixels[x, y]

            bits += format(red & 3, "02b")
            bits += format(blue & 3, "02b")

            pixel_number += 1

        if len(bits) == 8:
            result_bytes.append(int(bits, 2))

    try:
        text = bytes(result_bytes).decode("utf-8")
    except UnicodeDecodeError:
        text = bytes(result_bytes).decode("cp1251", errors="ignore")

    print("Декодированный текст из нового изображения:")
    print(text)


try:
    print("Лабораторная работа. Вариант 38.")
    print("1 — Декодировать сообщение из готового изображения")
    print("2 — Закодировать и декодировать свой текст")

    choice = input("Выберите действие: ")

    if choice == "1":
        image_name = input("Введите имя изображения, например new38.png: ")
        keys_name = input("Введите имя файла ключей, например keys38.txt: ")

        decode_blue_channel(image_name, keys_name)

    elif choice == "2":
        image_name = input("Введите имя исходного изображения: ")
        output_name = input("Введите имя нового изображения, например result.png: ")
        text = input("Введите текст для кодирования: ")

        byte_count = encode_text(image_name, output_name, text)

        if byte_count > 0:
            decode_own_image(output_name, byte_count)

    else:
        print("Ошибка: нужно выбрать 1 или 2.")

except FileNotFoundError:
    print("Ошибка: файл не найден.")

except Exception as error:
    print("Произошла ошибка, но программа не завершилась аварийно.")
    print("Описание ошибки:", error)