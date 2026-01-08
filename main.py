import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from config import TOKEN

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session)
print("Игровой бот запущен!")

game_state = {}

def send(uid, text="", attachment=None):
    vk.messages.send(
        user_id=uid,
        message=text,
        attachment=attachment or "",
        random_id=0
    )

def start_number_game(uid):
    secret = random.randint(1, 10)
    game_state[uid] = {"mode": "number", "secret": secret}
    send(uid, "Я загадал число от 1 до 10!")

def start_city_game(uid):
    cities = {
        "великие луки": "photo-234450844_456239027",
        "невель": "photo-234450844_456239028",
        "усвяты": "photo-234450844_456239030",
        "псков": "photo-234450844_456239029",
        "велиж": "photo-234450844_456239026"
    }
    city, photo_id = random.choice(list(cities.items()))
    game_state[uid] = {"mode": "сity_photo", "сity": city}
    send(uid, text="Угадай город по фотографии:", attachment=photo_id)

def start_truth_game(uid):
    facts = [
        ("У пингвинов есть колени.", "Правда"),
        ("Жирафы не умеют спать.", "Ложь"),
        ("Python назван в честь змеи.", "Ложь"),
    ]
    text, correct = random.choice(facts)
    game_state[uid] = {"mode": "quiz", "correct": correct}
    send(uid, f"Правда или ложь?\n{text}")

def process_game(uid, text):
    mode = game_state[uid]["mode"]

    if mode == "number":
        if not text.isdigit():
            send(uid, "Введи число от 1 до 10")
            return
        
        guess = int(text)
        secret = game_state[uid]["secret"]

        if guess == secret:
            send(uid, "Верно! ты угадал число")
            game_state.pop(uid)
        else:
            send(uid, "Неверно! Попробуй ещё раз")
        return
    
    if mode == "city_photo":
        correct = game_state[uid]["city"]

        if text.lower() == correct:
            send(uid, "Правильно")
        else:
            send(uid, f"Неверно! Это был: {correct.capitalize()}")

        game_state.pop(uid)
        return

    if mode == "quiz":
        correct = game_state[uid]["correct"]

        if text.lower() == correct:
            send(uid, "Верно!")
        else:
            send(uid, f"Неправильно! Ответ: {correct}")

        game_state.pop(uid)
        return
    
commands = {
    "игры": "menu",
    "1": start_number_game,
    "2": start_city_game,
    "3": start_truth_game
}

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        uid = event.user_id
        text = (event.text or "").strip().lower()

        if uid in game_state:
            process_game(uid, text)
            continue

        if text == "игры":
            send(uid,
                 "Вибери игру:\n"
                 "1 - Угадай игру\n"
                 "2 - Угадай город по фотографии"
                 "3 - Правда или ложь")
            continue

        if text in commands and callable(commands[text]):
            commands[text](uid)
            continue

        send(uid, "Я тебя не понял. Напиши: игры")