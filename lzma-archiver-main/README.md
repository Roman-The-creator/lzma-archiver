# LZMA-Архиватор

Простой архиватор файлов с поддержкой одиночного и мульти-архива на базе алгоритма LZMA (Python), с CLI-интерфейсом и авто-тестами.

## Возможности

- Сжатие одного файла (`.lzma`)
- Восстановление исходного файла из архива (`.lzma`)
- Сжатие набора файлов в мультииархив (`.lzma`, плюс `.meta`)
- Восстановление всех файлов из мультииархива
- CLI-режим для быстрой работы из терминала
- Автоматические тесты для проверки корректности

## Установка

Python 3.8+ (желательно 3.9+).

1. Склонируйте репозиторий или скачайте архив с исходным кодом
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

### Сжатие одного файла

```bash
python -m archiver compress путь/к/файлу.txt
```

### Распаковка одного файла

```bash
python -m archiver decompress путь/к/файлу.txt.lzma
```

### Сжатие нескольких файлов (через Python-интерфейс)

```python
from archiver.core import compress_files
compress_files(['file1.txt', 'file2.bin'], 'archive.lzma')
```

### Распаковка мультииархива (через Python-интерфейс)

```python
from archiver.core import decompress_all
decompress_all('archive.lzma', 'output_directory')
```

### Список содержимого архива

```python
from archiver.core import list_archive
print(list_archive('archive.lzma'))
```

## Тесты

Запуск всех тестов:

```bash
pytest tests/test_basic.py
```

## Зависимости

- Python 3.8+
- Стандартная библиотека lzma
- pytest (только для тестирования)

## Авторы

- Сухинин Артемий ФТ-201-2
- Михайлов Ярослав ФТ-201-2



