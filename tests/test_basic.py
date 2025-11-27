from pathlib import Path
import os

import pytest

from archiver.core import (
    compress_file,
    decompress_file,
    compress_files,
    decompress_all,
    list_archive,
)


def test_text_roundtrip(tmp_path: Path):
    src = tmp_path / "hello.txt"
    src.write_text("hello world\n" * 5, encoding="utf-8")

    archive = compress_file(src)
    restored = decompress_file(archive)

    assert restored.exists()
    assert restored.read_text(encoding="utf-8") == src.read_text(encoding="utf-8")


def test_binary_roundtrip(tmp_path: Path):
    src = tmp_path / "data.bin"
    original_data = os.urandom(1500)
    src.write_bytes(original_data)

    archive = compress_file(src)
    restored = decompress_file(archive)

    assert restored.read_bytes() == original_data


def test_multi_archive(tmp_path: Path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.bin"
    f1.write_text("AAA", encoding="utf-8")
    f2.write_bytes(b"\x01\x02\x03")

    archive = tmp_path / "pack.lzma"
    compress_files([f1, f2], archive)

    info = list_archive(archive)
    assert len(info) == 2
    assert {i.name for i in info} == {"a.txt", "b.bin"}

    out_dir = tmp_path / "out"
    extracted = decompress_all(archive, out_dir)
    assert len(extracted) == 2

    assert (out_dir / "a.txt").read_text(encoding="utf-8") == "AAA"
    assert (out_dir / "b.bin").read_bytes() == b"\x01\x02\x03"


def test_broken_archive(tmp_path: Path):
    bad = tmp_path / "broken.lzma"
    bad.write_bytes(b"NOT A VALID ARCHIVE")

    # при распаковке сломанного архива должна быть ошибка
    with pytest.raises(Exception):
        decompress_file(bad)
