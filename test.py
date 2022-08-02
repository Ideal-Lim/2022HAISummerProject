from datetime import datetime
import time

today_now = datetime.now()
t_9 = today_now.replace(hour=9, minute=0, second=0, microsecond=0)
print(today_now, t_9)
time.sleep(2)