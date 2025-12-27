import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import TOKEN

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session)
print("Бот слишком пог")

def send(user_id, text=None, attachment=None):
    vk.messages.send(
        user_id=user_id,
        message=text or "",
        attachment=attachment or "",
        random_id=0
    )

PHOTOS = [
    "photo-234450844_456239025",
    "photo-234450844_456239024",
    "photo-234450844_456239023",
    "photo-234450844_456239022",
    "photo-234450844_456239021",
]

POG = "photo-234450844_456239021"

def cmd_meme():
    return "Я люблю Вк 💕", POG

def cmd_random():
    random_photos = random.choice(PHOTOS)
    return "Случайная картинка", random_photos

def cmd_start():
    return "Привет! Выбери команду:\n/meme - мем\n/random - случайная картинка", None

def cmd_help():
    return "Доступные команды:\n/meme - мем\n/random - случайная картинка", None

commands = {
    "/meme": cmd_meme,
    "/random": cmd_random,
    "мем": cmd_meme,
    "рандомная картинка": cmd_random,
    "/start": cmd_start,
    "/help": cmd_help,
}

keyboard = VkKeyboard(one_time=False)
keyboard.add_button('мем', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('рандомная картинка', color=VkKeyboardColor.PRIMARY)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = (event.text or "").strip().lower()

        if text in commands:
            msg, attach = commands[text]()
            send(user_id, text=msg, attachment=attach)
        else:
            send(user_id, "Не знаю такой команды. Напиши /help")
