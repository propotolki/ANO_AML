# Бот Федор для ВКонтакте

Бот для мероприятия АНО "Академия Молодых Лидеров"

## Функционал

- ✅ Приветственное сообщение
- ✅ Проверка подписки на группу
- ✅ Регистрация с выдачей цветов
- ✅ Информация о программе
- ✅ Игра с 8 эко-точками
- ✅ Временные кнопки (5 ноября 13:00-19:00)

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` по примеру ниже и заполните токен и ID группы:
   ```env
   VK_TOKEN=ваш_токен_группы
   GROUP_ID=ваш_numeric_group_id
   ```
4. Запустите бота:
   ```bash
   python main.py
   ```

## Переменные окружения

- VK_TOKEN — сервисный токен сообщества с доступом к сообщениям
- GROUP_ID — числовой ID сообщества (без "club")

## Хранилище

Данные пользователей хранятся в `data/users.json` (создается автоматически).

## Описания эко-точек

Бот читает описания из `data/points.json`, если файл существует. Формат:
```json
{
  "1": "Текст для точки 1",
  "2": "Текст для точки 2",
  "3": "...",
  "4": "...",
  "5": "...",
  "6": "...",
  "7": "...",
  "8": "..."
}
```
Если файла нет — используются дефолтные описания. Чтобы использовать текст из вашего документа, скопируйте его в `data/points.json` в указанном формате.

---

## VK Mini App (SPA)

В каталоге `vk_app/` находится минимальное мини‑приложение для ВКонтакте (статическая SPA) с цветовой палитрой, вдохновленной презентацией АНО. Раздаётся через Flask-приложение `webapp.py`.

Запуск локально:
```bash
python webapp.py
# откройте http://localhost:8000
```

### Деплой SPA на PythonAnywhere (веб‑приложение)

1) Создайте виртуальное окружение и установите зависимости
```bash
python3.10 -m venv ~/.venvs/ano-aml
source ~/.venvs/ano-aml/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2) Создайте Web app (Manual configuration, Python 3.10), укажите virtualenv `~/.venvs/ano-aml`.

3) В WSGI‑файле добавьте путь проекта и загрузите приложение:
```python
import sys
path = '/home/<user>/apps/ANO_AML'
if path not in sys.path:
    sys.path.append(path)
from webapp import app as application
```

4) Перезагрузите веб‑приложение, откройте выданный HTTPS‑URL — загрузится SPA из `vk_app/`.

Справка о PythonAnywhere и веб-хостинге: [pythonanywhere.com](https://www.pythonanywhere.com)

---

## Подготовка к публикации на GitHub

Файлы настроены для репозитория:
- `.gitignore` — игнорирует виртуальные окружения, логи, секреты и `data/users.json`
- `data/.gitkeep` — фиксирует пустую директорию `data/` в репозитории

### Шаги публикации в GitHub (под логином `propotolki`)

1) Инициализировать git в корне проекта:
```bash
git init
```

2) Добавить файлы и первый коммит:
```bash
git add .
git commit -m "Initial commit: VK bot + Mini App + Flask web"
```

3) Создать пустой репозиторий в GitHub (например, `ANO_AML`) под пользователем `propotolki`.

4) Привязать удалённый репозиторий и запушить:
```bash
git remote add origin https://github.com/propotolki/ANO_AML.git
git branch -M main
git push -u origin main
```

GitHub — главная страница: [github.com](https://github.com)

---

## Заметки по продакшн‑развёртыванию бота (LongPoll)

Для постоянной работы LongPoll на PythonAnywhere используйте Always‑on task (платные тарифы). Команда запуска:
```bash
/home/<user>/.venvs/ano-aml/bin/python /home/<user>/apps/ANO_AML/main.py
```

Описание сервиса и масштабирование — см. главную страницу: [pythonanywhere.com](https://www.pythonanywhere.com)
