import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import datetime
import os
import logging
from typing import Dict, Any
import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VkBot')

class JSONStorage:
    """Класс для работы с JSON хранилищем"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path or config.DATA_FILE
        self.ensure_data_dir()
        self.init_storage()
    
    def ensure_data_dir(self):
        """Создает папку data если её нет"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def init_storage(self):
        """Инициализирует хранилище если файла нет"""
        if not os.path.exists(self.file_path):
            initial_data = {
                "users": {},
                "color_counter": 0,
                "teams": {
                    "0": 1, "1": 2, "2": 3, "3": 4,
                    "4": 5, "5": 6, "6": 7, "7": 8
                },
                "settings": {
                    "game_active": False
                }
            }
            self.save_data(initial_data)
            logger.info("Инициализировано новое хранилище данных")
    
    def load_data(self) -> Dict[str, Any]:
        """Загружает данные из JSON файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return {"users": {}, "color_counter": 0, "teams": {}, "settings": {"game_active": False}}
    
    def save_data(self, data: Dict[str, Any]):
        """Сохраняет данные в JSON файл"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False

class VkBotFedor:
    def __init__(self, token: str, group_id: str):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.vk = self.vk_session.get_api()
        self.storage = JSONStorage(config.DATA_FILE)
        
        # Настройки бота
        self.colors = ['🔴 Красный', '🔵 Синий', '🟢 Зеленый', '🟡 Желтый', 
                      '🟣 Фиолетовый', '🟠 Оранжевый', '⚫ Черный', '⚪ Белый']
        
        # Время активации игры
        self.game_start_time = datetime.datetime(2025, 11, 5, 13, 0, 0)
        self.game_end_time = datetime.datetime(2025, 11, 5, 19, 0, 0)
        
        logger.info("Бот Федор инициализирован")

        # Описания точек: подгрузим из JSON если доступно
        self.point_descriptions = self.load_point_descriptions()

    def load_point_descriptions(self) -> Dict[int, str]:
        """Загружает описания точек из data/points.json, иначе возвращает дефолтные."""
        try:
            path = os.path.join('data', 'points.json')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                # Преобразуем ключи в int
                return {int(k): v for k, v in raw.items()}
        except Exception as e:
            logger.error(f"Ошибка загрузки описаний точек: {e}")
        # Дефолтные описания (заменим при загрузке из файла)
        return {
            1: "🌱 Точка 1: Знакомство и командообразование - здесь вы узнаете друг друга лучше",
            2: "🎯 Точка 2: Лидерские качества - развиваем лидерский потенциал",
            3: "📊 Точка 3: Проектная деятельность - учимся создавать проекты",
            4: "💬 Точка 4: Коммуникации - искусство эффективного общения",
            5: "🧠 Точка 5: Стратегическое мышление - планируем наперед",
            6: "⚡ Точка 6: Решение проблем - находим нестандартные решения",
            7: "💡 Точка 7: Инновации - создаем новое",
            8: "🏆 Точка 8: Итоги и планы - подводим результаты и строим планы"
        }

    def get_user_info(self, user_id: int) -> Dict[str, str]:
        """Получает информацию о пользователе из VK"""
        try:
            user_info = self.vk.users.get(user_ids=user_id, fields='first_name,last_name')[0]
            return {
                'first_name': user_info.get('first_name', 'Друг'),
                'last_name': user_info.get('last_name', '')
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе {user_id}: {e}")
            return {'first_name': 'Друг', 'last_name': ''}

    def check_subscription(self, user_id: int) -> bool:
        """Проверяет подписку пользователя на группу"""
        try:
            result = self.vk.groups.isMember(
                group_id=config.GROUP_ID,
                user_id=user_id
            )
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка проверки подписки для {user_id}: {e}")
            return False

    def get_next_color(self) -> tuple:
        """Возвращает следующий цвет по порядку"""
        data = self.storage.load_data()
        color_index = data["color_counter"] % len(self.colors)
        color = self.colors[color_index]
        
        # Обновляем счетчик
        data["color_counter"] = (color_index + 1) % len(self.colors)
        self.storage.save_data(data)
        
        return color, color_index

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Получает данные пользователя"""
        data = self.storage.load_data()
        return data["users"].get(str(user_id))

    def save_user_data(self, user_id: int, user_data: Dict[str, Any]):
        """Сохраняет данные пользователя"""
        data = self.storage.load_data()
        data["users"][str(user_id)] = user_data
        return self.storage.save_data(data)

    def send_message(self, user_id: int, message: str, keyboard=None):
        """Отправляет сообщение пользователю"""
        try:
            params = {
                'user_id': user_id,
                'message': message,
                'random_id': 0
            }
            if keyboard:
                params['keyboard'] = keyboard.get_keyboard()
            
            self.vk.messages.send(**params)
            logger.info(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

    # === КЛАВИАТУРЫ ===
    def create_main_keyboard(self):
        """Клавиатура главного меню"""
        keyboard = VkKeyboard(one_time=False)
        now = datetime.datetime.now()
        if self.game_start_time <= now <= self.game_end_time:
            keyboard.add_button('Вернуться назад', color=VkKeyboardColor.NEGATIVE)
        else:
            keyboard.add_button('Хочу пройти регистрацию', color=VkKeyboardColor.PRIMARY)
        return keyboard

    def create_registration_keyboard(self):
        """Клавиатура после регистрации"""
        keyboard = VkKeyboard(one_time=False)
        now = datetime.datetime.now()
        if self.game_start_time <= now <= self.game_end_time:
            # Во время окна игры заменяем все кнопки на одну — "Вернуться назад"
            keyboard.add_button('Вернуться назад', color=VkKeyboardColor.NEGATIVE)
        else:
            keyboard.add_button('Зачем мне цвет', color=VkKeyboardColor.SECONDARY)
            keyboard.add_button('Узнать программу', color=VkKeyboardColor.SECONDARY)
        return keyboard

    def create_back_keyboard(self):
        """Клавиатура с кнопкой Начать игру"""
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Начать игру', color=VkKeyboardColor.POSITIVE)
        return keyboard

    def create_game_keyboard(self):
        """Клавиатура во время игры"""
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Готово', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Вернуться назад', color=VkKeyboardColor.NEGATIVE)
        return keyboard

    # === ОБРАБОТЧИКИ КОМАНД ===
    def handle_start(self, user_id: int):
        """Обработчик команды начала"""
        user_info = self.get_user_info(user_id)
        first_name = user_info['first_name']
        
        welcome_message = f"""Привет, {first_name}! Меня зовут Федор. Ты мог меня видеть в роликах, в нашей группе, а сегодня я тебе расскажу, что делать на мероприятии"""
        
        self.send_message(user_id, welcome_message, self.create_main_keyboard())

    def handle_registration(self, user_id: int):
        """Обработчик регистрации"""
        user_info = self.get_user_info(user_id)
        first_name = user_info['first_name']
        
        # Проверяем подписку
        if not self.check_subscription(user_id):
            message = f"""{first_name}, я очень расстроен, что ты не подписан на нашу группу, ведь там есть ролики со мной и много всего интересного, подпишись, пожалуйста: https://vk.com/ano_mol_lid"""
            self.send_message(user_id, message, self.create_main_keyboard())
            return

        # Проверяем существующего пользователя
        existing_user = self.get_user_data(user_id)
        
        if existing_user:
            # Пользователь уже зарегистрирован
            color = existing_user['color']
            color_square = self.get_color_square(color)
            message = f"""{first_name}, я очень рад тебя видеть снова! Ты уже зарегистрирован в системе.

Твой цвет: {color}
{color_square}

Мы рады тебя видеть на открытии АНО "Академия Молодых Лидеров"."""
        else:
            # Новый пользователь
            color, color_index = self.get_next_color()
            color_square = self.get_color_square(color)
            
            user_data = {
                'user_id': user_id,
                'first_name': first_name,
                'last_name': user_info['last_name'],
                'color': color,
                'color_index': color_index,
                'registration_date': datetime.datetime.now().isoformat(),
                'is_subscribed': True
            }
            
            self.save_user_data(user_id, user_data)
            
            message = f"""{first_name}, я очень рад, что ты подписан на нашу группу!

Мы рады тебя видеть на открытии АНО "Академия Молодых Лидеров".

Тебе присвоен цвет: {color}
{color_square}"""

        self.send_message(user_id, message, self.create_registration_keyboard())

    def get_color_square(self, color: str) -> str:
        """Возвращает цветной квадрат для сообщения"""
        color_emojis = {
            '🔴 Красный': '🟥',
            '🔵 Синий': '🟦', 
            '🟢 Зеленый': '🟩',
            '🟡 Желтый': '🟨',
            '🟣 Фиолетовый': '🟪',
            '🟠 Оранжевый': '🟧',
            '⚫ Черный': '⬛',
            '⚪ Белый': '⬜'
        }
        return color_emojis.get(color, '⬜')

    def handle_why_color(self, user_id: int):
        """Обработчик кнопки 'Зачем мне цвет'"""
        user_info = self.get_user_info(user_id)
        first_name = user_info['first_name']
        message = (
            f"{first_name},\n\n"
            "🎯 Цвет и номер команды — ваши суперсилы!\n\n"
            "Цвет — это ваш флаг 🎨\n\n"
            "Сразу видно, где свои.\n\n"
            "Создаёт ваш уникальный стиль.\n\n"
            "Помогает не заблудиться среди эко-точек.\n\n"
            "Номер — это ваш игровой чип 🎲\n\n"
            "По нему определяют очерёдность.\n\n"
            "На него записываются все ваши победы.\n\n"
            "Это ваш билет в розыгрыш мерча и пьедестал почёта!\n\n"
            "Короче: Цвет — ваше лицо, а номер — ваш пропуск к победе! 🏆"
        )
        
        self.send_message(user_id, message, self.create_registration_keyboard())

    def handle_program(self, user_id: int):
        """Обработчик кнопки 'Узнать программу'"""
        user_info = self.get_user_info(user_id)
        first_name = user_info['first_name']
        
        pdf_url = "https://vk.cc/cQXLrM"
        message = f"""{first_name}, вот программа нашего мероприятия:
{pdf_url}

Скачай программу и будь в курсе всех событий! 📋"""
        
        self.send_message(user_id, message, self.create_registration_keyboard())

    def handle_back_button(self, user_id: int):
        """Обработчик кнопки 'Вернуться назад'"""
        message = "Хочешь начать игру?"
        self.send_message(user_id, message, self.create_back_keyboard())

    def handle_start_game(self, user_id: int):
        """Обработчик кнопки 'Начать игру'"""
        user_data = self.get_user_data(user_id)
        
        if not user_data:
            self.send_message(user_id, "Сначала пройди регистрацию!", self.create_main_keyboard())
            return

        color_index = user_data['color_index']
        color = user_data['color']
        
        # Получаем текущую точку для команды (не продвигаем, пока не нажмут "Готово")
        data = self.storage.load_data()
        current_point = data["teams"].get(str(color_index), 1)
        next_point = current_point % 8 + 1

        message = f"""🎮 Начинаем игру!

Тебе необходимо пройти 8 эко точек, которые символизируют развитие внутри АНО. 

Твоя команда: {color}
Текущая точка: {current_point} из 8
Следующая точка: {next_point}

{self.point_descriptions.get(current_point, '')}

Двигайся по точкам, которые я тебе укажу. Каждая команда должна пройти все 8 точек, и на каждой точке может быть только одна команда!"""

        self.send_message(user_id, message, self.create_game_keyboard())

    def handle_point_done(self, user_id: int):
        """Обработчик кнопки 'Готово' — продвигает команду на следующую точку и отправляет её описание."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            self.send_message(user_id, "Сначала пройди регистрацию!", self.create_main_keyboard())
            return

        color_index = user_data['color_index']
        color = user_data['color']

        data = self.storage.load_data()
        current_point = data["teams"].get(str(color_index), 1)
        next_point = current_point % 8 + 1

        # Продвигаем команду
        data["teams"][str(color_index)] = next_point
        self.storage.save_data(data)

        message = f"""✅ Точка {current_point} завершена!

Твоя команда: {color}
Новая текущая точка: {next_point} из 8
Следующая точка: {(next_point % 8) + 1}

{self.point_descriptions.get(next_point, '')}

Нажми "Готово", когда завершите эту точку."""

        self.send_message(user_id, message, self.create_game_keyboard())

    def run(self):
        """Запускает бота"""
        logger.info("Бот Федор запущен...")
        
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text'].lower()
                
                logger.info(f"Получено сообщение от {user_id}: {text}")
                
                try:
                    if text == 'начать':
                        self.handle_start(user_id)
                    elif text == 'хочу пройти регистрацию':
                        self.handle_registration(user_id)
                    elif text == 'зачем мне цвет':
                        self.handle_why_color(user_id)
                    elif text == 'узнать программу':
                        self.handle_program(user_id)
                    elif text == 'вернуться назад':
                        now = datetime.datetime.now()
                        if self.game_start_time <= now <= self.game_end_time:
                            self.handle_back_button(user_id)
                        else:
                            self.send_message(user_id, "Эта функция будет доступна 5 ноября с 13:00 до 19:00", self.create_registration_keyboard())
                    elif text == 'начать игру':
                        now = datetime.datetime.now()
                        if self.game_start_time <= now <= self.game_end_time:
                            self.handle_start_game(user_id)
                        else:
                            self.send_message(user_id, "Игра будет доступна 5 ноября с 13:00 до 19:00", self.create_registration_keyboard())
                    elif text == 'готово':
                        now = datetime.datetime.now()
                        if self.game_start_time <= now <= self.game_end_time:
                            self.handle_point_done(user_id)
                        else:
                            self.send_message(user_id, "Игра будет доступна 5 ноября с 13:00 до 19:00", self.create_registration_keyboard())
                    else:
                        # Ответ на неизвестные команды
                        self.send_message(user_id, "Используй кнопки для навигации 😊", self.create_main_keyboard())
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения от {user_id}: {e}")
                    self.send_message(user_id, "Произошла ошибка. Попробуй еще раз.", self.create_main_keyboard())