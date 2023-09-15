from datetime import datetime
import pytz

local_time = datetime.now()
kiev_time = datetime.now(pytz.timezone("Europe/Kiev"))

print(f"Local time: {local_time}")
print(f"Kiev time: {kiev_time}")
