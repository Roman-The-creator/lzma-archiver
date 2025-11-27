from __future__ import annotations

import json
import lzma
from dataclasses import dataclass
from pathlib import Path


# ---------- ОДИН ФАЙЛ: compress_file / decompress_file ----------


def compress_file(path: str | Path) -> Path:
    """Сжать один файл в <имя>.lzma."""
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(src)

    dst = src.with_suffix(src.suffix + ".lzma")

    data = src.read_bytes()
    compressed = lzma.compress(data)

    dst.write_bytes(compressed)
    return dst


def decompress_file(path: str | Path) -> Path:
    """Распаковать один .lzma-файл обратно."""
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(src)

    compressed = src.read_bytes()
    data = lzma.decompress(compressed)

    # просто убираем .lzма в конце
    if src.suffix == ".lzma":
        dst = src.with_suffix("")
    else:
        dst = src.with_name(src.name + ".restored")

    dst.write_bytes(data)
    return dst


# ---------- MULTI-АРХИВ: compress_files / list_archive / decompress_all ----------

@dataclass
class ArchiveEntry:
    name: str
    size: int  # размер сжатого блока в архиве


def compress_files(files: list[str | Path], archive_path: str | Path) -> Path:
    """
    Сжать несколько файлов в один архив.

    Формат архива:
        [2 байта] длина имени (big-endian)
        [N байт]  имя файла (UTF-8)
        [..]      сжатые данные LZMA

    Метаданные (список файлов и размеров сжатых блоков) пишем
    в JSON-файл рядом: <archive>.meta
    """
    archive_path = Path(archive_path)
    metadata: list[dict[str, int | str]] = []

    with archive_path.open("wb") as archive:
        for file in files:
            src = Path(file)
            if not src.is_file():
                raise FileNotFoundError(src)

            data = src.read_bytes()
            compressed = lzma.compress(data)

            name_bytes = src.name.encode("utf-8")
            name_len = len(name_bytes)

            # пишем длину имени, имя и сжатые данные
            archive.write(name_len.to_bytes(2, "big"))
            archive.write(name_bytes)
            archive.write(compressed)

            metadata.append(
                {
                    "name": src.name,
                    "size": len(compressed),
                }
            )

    # сохраняем метаданные отдельно
    meta_path = archive_path.with_suffix(archive_path.suffix + ".meta")
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")

    return archive_path


def list_archive(archive_path: str | Path) -> list[ArchiveEntry]:
    """Прочитать .meta и вернуть список объектов ArchiveEntry."""
    archive_path = Path(archive_path)
    meta_path = archive_path.with_suffix(archive_path.suffix + ".meta")

    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    return [ArchiveEntry(name=m["name"], size=m["size"]) for m in metadata]


def decompress_all(archive_path: str | Path, output_dir: str | Path) -> list[Path]:
    """
    Распаковать все файлы из multi-архива в указанную директорию.
    Опираться на .meta-файл и на порядок записей в самом архиве.
    """
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = list_archive(archive_path)
    result_paths: list[Path] = []

    with archive_path.open("rb") as archive:
        for entry in entries:
            name = entry.name
            comp_size = entry.size

            # читаем длину имени и само имя, чтобы сдвинуться по файлу
            name_len_bytes = archive.read(2)
            if len(name_len_bytes) < 2:
                raise ValueError("Повреждён архив: не удалось прочитать длину имени")

            name_len = int.from_bytes(name_len_bytes, "big")
            archive.read(name_len)  # пропускаем имя

            # читаем ровно comp_size байт сжатых данных
            compressed = archive.read(comp_size)
            if len(compressed) < comp_size:
                raise ValueError("Повреждён архив: блок данных не дочитан")

            data = lzma.decompress(compressed)

            out_path = output_dir / name
            out_path.write_bytes(data)
            result_paths.append(out_path)

    return result_paths
