import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteer_rand.settings")
django.setup()
import pandas as pd
from datetime import datetime
from call_manager.models import Recipient, Item


def convert_date_format(date_value, original_format='%d/%m/%Y', target_format="%Y-%m-%d"):
    """
    Форматирует строку даты или объект datetime в строку с нужным форматом.

    :param date_value: строка даты или объект datetime
    :param original_format: исходный формат даты (предполагается для строк)
    :param target_format: желаемый формат даты
    :return: дата в желаемом формате
    """
    if isinstance(date_value, str):
        try:
            # Преобразование строки даты в объект datetime
            date_obj = datetime.strptime(date_value, original_format)
            # Преобразование объекта datetime обратно в строку с нужным форматом
            return date_obj.strftime(target_format)
        except Exception as e:
            print(f"Error converting date: {e}")
            return None
    elif isinstance(date_value, datetime):
        try:
            return date_value.strftime(target_format)
        except Exception as e:
            print(f"Error converting date: {e}")
            return None
    else:
        print(f"Unexpected date type: {type(date_value)}")
        return None


def import_missing_phone_numbers(file_path):
    df = pd.read_excel(file_path)
    items_list = ["powerbank", "headlamp", "thermos", "blanket", "soap"]
    missing_numbers_count = 0

    for _, row in df.iterrows():
        print(f"Processing row {_}: Phone: {row['_phone']}")
        try:
            if pd.isna(row["_phone"]):
                print("Skipping due to NaN phone.")
                continue

            phone = str(row["_phone"]).strip()
            recipient, created = Recipient.objects.get_or_create(phone_number=phone)

            if created:
                missing_numbers_count += 1
                print(f"Added new recipient with phone {phone}")
            else:
                print(f"Recipient with phone {phone} already exists!")

                recipient.name = row["name"] if "name" in df.columns and not pd.isna(row["name"]) else ""
                recipient.state = row["state"]
                recipient.place = row["place"]
                recipient.date_distribution = convert_date_format(row["date"]) if "date" in df.columns else None
                recipient.gender = row["gender"]
                recipient.age = row["age"]
                recipient.volunteer = row["volunteers"]
                recipient.save()

                for item_name in items_list:
                    if row[item_name] == 1:
                        item, _ = Item.objects.get_or_create(name=item_name)
                        recipient.items_received.add(item)
                        print(f"Assigned item {item_name} to recipient {phone}")
        except Exception as e:
            print(f"Error processing row {row.name}: {e}")

    print(f"\nTotal missing phone numbers added: {missing_numbers_count}")


file_path = "static/data/volonterska_phone.xlsx"
import_missing_phone_numbers(file_path)
