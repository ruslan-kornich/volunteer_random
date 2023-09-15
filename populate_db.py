import os
import django

# Указываем настройки для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_rand.settings")
django.setup()

import pandas as pd
from call_manager.models import Recipient, Item


def import_data_from_excel(file_path):
    try:
        # Загружаем данные из Excel файла
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return

    # Список товаров для проверки в DataFrame
    items_list = ["powerbank", "headlamp", "thermos", "blanket", "soap"]

    for _, row in df.iterrows():
        try:
            phone = str(row["_phone"]).strip()

            # Проверяем, существует ли получатель с данным номером телефона
            recipient, created = Recipient.objects.get_or_create(phone_number=phone)

            # Если получатель был только что создан, заполняем его данными
            if created:
                print(f"Added new recipient with phone {phone}")
                recipient.name = ""  # можно добавить имя, если есть колонка с именем
                recipient.state = row["state"]
                recipient.place = row["place"]
                recipient.date_distribution = row["date"]
                recipient.gender = row["gender"]
                recipient.age = row["age"]
                recipient.volunteer = row["volunteers"]
                recipient.save()

            # Добавляем вещи, которые были выданы
            for item_name in items_list:
                if row[item_name] == 1:
                    item, _ = Item.objects.get_or_create(name=item_name)
                    recipient.items_received.add(item)
                    print(f"Assigned item {item_name} to recipient {phone}")

        except Exception as e:
            print(f"An error occurred while processing row: {row}. Error: {e}")

    print("Data has been imported successfully!")


# Путь к вашему файлу Excel
file_path = "static/data/Items_with_numbers.xlsx"
try:
    import_data_from_excel(file_path)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
