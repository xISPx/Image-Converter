from PIL import Image, ImageOps
from pathlib import Path

valid_ext = ['.jpg', '.jpeg', '.png', '.bmp']

def get_user_settings():
    """Запрашивает настройки у пользователя"""
    print("\n=== Настройки конвертации ===")
    
    # Выбор формата
    formats = {
        '1': ('JPEG', 'jpg', {'quality': 85}),
        '2': ('PNG', 'png', {'compress_level': 6}),
        '3': ('BMP', 'bmp', {})
    }
    
    print("Выберите формат для сохранения:")
    for key, value in formats.items():
        print(f"{key}. {value[0]} ({value[1]})")
    
    while True:
        choice = input("Ваш выбор (1-3): ")
        if choice in formats:
            ext = formats[choice][1]
            params = formats[choice][2]
            break
        print("Некорректный ввод! Попробуйте снова.")

    # Дополнительные параметры только для JPEG
    if choice == '1':
        while True:
            try:
                quality = int(input(f"Качество JPEG (1-100): "))
                if 1 <= quality <= 100:
                    params['quality'] = quality
                    break
                raise ValueError
            except:
                print("Некорректное значение! Используйте число от 1 до 100.")

    # Размер изображения
    while True:
        try:
            width = int(input("Максимальная ширина (пиксели): "))
            height = int(input("Максимальная высота (пиксели): "))
            if width > 0 and height > 0:
                break
            raise ValueError
        except:
            print("Некорректные размеры! Используйте положительные числа.")

    # Дополнительные настройки
    keep_aspect = input("Сохранять пропорции? (y/n): ").lower() == 'y'
    auto_rotate = input("Автоматически поворачивать вертикальные фото? (y/n): ").lower() == 'y'
    
    return {
        'ext': ext,
        'format': formats[choice][0],
        'size': (width, height),
        'params': params,
        'keep_aspect': keep_aspect,
        'auto_rotate': auto_rotate
    }

def process_images(settings):
    """Обрабатывает изображения с выбранными настройками"""
    script_dir = Path(__file__).parent.resolve()
    output_dir = script_dir / "converted"
    output_dir.mkdir(parents=True, exist_ok=True)

    processed = 0

    for file_path in script_dir.iterdir():
        try:
            if not file_path.is_file() or file_path.suffix.lower() not in valid_ext:
                continue

            with Image.open(file_path) as img:
                # Коррекция ориентации по EXIF
                img = ImageOps.exif_transpose(img)
                
                # Автоматический поворот вертикальных фото
                if settings['auto_rotate'] and img.height > img.width:
                    img = img.rotate(90, expand=True)
                
                # Конвертация прозрачности
                if img.mode in ('RGBA', 'P') and settings['format'] != 'PNG':
                    img = img.convert('RGB')
                
                # Изменение размера
                if settings['keep_aspect']:
                    img.thumbnail(settings['size'])
                else:
                    img = img.resize(settings['size'])
                
                # Сохранение
                output_path = output_dir / f"{file_path.stem}_converted.{settings['ext']}"
                img.save(output_path, settings['format'], **settings['params'])
                processed += 1
                print(f"Конвертировано: {file_path.name} → {output_path.name}")

        except Exception as e:
            print(f"Ошибка при обработке {file_path.name}: {str(e)}")

    print(f"\nГотово! Обработано файлов: {processed}")
    print(f"Результаты сохранены в: {output_dir}")

if __name__ == "__main__":
    print("=== Image Converter ===")
    print("Найденные изображения в текущей папке:")
    
    script_dir = Path(__file__).parent.resolve()
    image_files = [f.name for f in script_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_ext]
    
    if not image_files:
        print("Нет изображений для обработки!")
        exit()
    
    for img in image_files:
        print(f"- {img}")
    
    if input("\nНачать конвертацию? (y/n): ").lower() == 'y':
        settings = get_user_settings()
        process_images(settings)
    else:
        print("Отменено пользователем.")