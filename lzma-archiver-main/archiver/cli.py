import argparse
import lzma
from .core import compress_file, decompress_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Простой архиватор на LZMA"
    )

    parser.add_argument(
        "mode",
        choices=["compress", "decompress"],
        help="Режим работы: compress — сжать файл, decompress — распаковать архив",
    )
    parser.add_argument(
        "input",
        help="Путь к входному файлу (для compress — исходный файл, для decompress — архив)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Путь к выходному файлу (если не указан, имя будет выбрано автоматически)",
    )

    args = parser.parse_args()

    try:
        if args.mode == "compress":
            out_path = compress_file(args.input, args.output)
            print(f"Файл сжат в: {out_path}")
        else:
            out_path = decompress_file(args.input, args.output)
            print(f"Файл распакован в: {out_path}")
    except FileNotFoundError:
        print("Ошибка: входной файл не найден.")
    except lzma.LZMAError:
        print("Ошибка: файл не является корректным LZMA-архивом.")
    except ValueError as e:
        print(f"Ошибка формата архива: {e}")
