import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print(repr(url))   # покажет скрытые символы