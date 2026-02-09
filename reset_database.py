#!/usr/bin/env python3
import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from app import app, db


def main():
    print("=" * 60)
    print("ПОЛНОЕ ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ ШКОЛЬНОГО ПИТАНИЯ")
    print("=" * 60)

    with app.app_context():
        db_file = current_dir / 'school_food.db'
        if db_file.exists():
            print(f"🗑️  Удаляем старую базу данных: {db_file}")
            try:
                os.remove(db_file)
            except Exception as e:
                print(f"⚠️  Ошибка удаления файла: {e}")

        print("🗑️  Удаляем все таблицы...")
        db.drop_all()

        print("🆕 Создаем новые таблицы...")
        db.create_all()

        from app import create_tables
        print("\n📊 Заполняем начальными данными...")
        create_tables()

        print("\n" + "=" * 60)
        print("✅ БАЗА ДАННЫХ УСПЕШНО ПЕРЕСОЗДАНА!")
        print("=" * 60)
        print("\n✅ Все данные сброшены")
        print("✅ Созданы чистые таблицы")
        print("✅ Добавлены только начальные данные")


if __name__ == '__main__':
    main()