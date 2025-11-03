import os
from dotenv import load_dotenv

load_dotenv()

# Настройки VK
VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

# Проверка обязательных переменных
if not VK_TOKEN or not GROUP_ID:
    raise ValueError("Не установлены VK_TOKEN и GROUP_ID в переменных окружения")

# Настройки бота
# Делаем путь к файлу данных абсолютным, чтобы работать из любого cwd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'users.json')