from datetime import datetime

import pytz

day = datetime.today().weekday()

my_date = datetime.now(pytz.timezone('Europe/Moscow')).time()

print(my_date)
