from pathlib import Path
from typing import Optional
import lzma


def compress_file(input_path: str, output_path: Optional[str] = None) -> Path:
    in_path = Path(input_path)
    if not in_path.is_file():
        raise FileNotFoundError(f"Нет такого файла: {in_path}")

    if output_path is None:
        out_path = in_path.with_suffix(in_path.suffix + ".lzma")
    else:
        out_path = Path(output_path)

    data = in_path.read_bytes()
    compressed = lzma.compress(data)

    filename_bytes = in_path.name.encode("utf-8")
    filename_len = len(filename_bytes)

    with open(out_path, "wb") as f:
        f.write(filename_len.to_bytes(4, "big"))
        f.write(filename_bytes)
        f.write(compressed)

    return out_path


def decompress_file(input_path: str, output_path: Optional[str] = None) -> Path:
    in_path = Path(input_path)
    if not in_path.is_file():
        raise FileNotFoundError(f"Нет такого файла: {in_path}")

    with open(in_path, "rb") as f:
        filename_len_bytes = f.read(4)
        if len(filename_len_bytes) < 4:
            raise ValueError("Файл повреждён или не является корректным архивом LZMA с метаданными")
        filename_len = int.from_bytes(filename_len_bytes, "big")

        filename_bytes = f.read(filename_len)
        if len(filename_bytes) < filename_len:
            raise ValueError("Файл повреждён или не является корректным архивом LZMA с метаданными")
        original_filename = filename_bytes.decode("utf-8")

        compressed = f.read()
        data = lzma.decompress(compressed)

    if output_path is None:
        out_path = in_path.with_name(original_filename)
    else:
        out_path = Path(output_path)

    out_path.write_bytes(data)
    return out_path
