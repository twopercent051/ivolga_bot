import re

regex = r"(?P<domain>\w+\.\w{2,3})"

test_str = ("Hello, pythonworld.ru!\n"
  "Checking гто.рф\n"
  "microsoft.com")

matches = re.finditer(regex, test_str, re.MULTILINE)

for r in matches:
    print(r)
