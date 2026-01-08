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
    vk.messages.send(user_id=uid,
                     message=text,
                     attachment=attachment or "",
                     random_id=0)


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
    # ИСПРАВЛЕНО: английская 'c' вместо русской 'с'
    game_state[uid] = {"mode": "city_photo", "city": city}
    send(uid, text="Угадай город по фотографии:", attachment=photo_id)


def start_truth_game(uid):
    facts = [
        ("У пингвинов есть колени.", "правда"),
        ("Жирафы не умеют спать.", "ложь"),
        ("Python назван в честь змеи.", "ложь"),
    ]
    text, correct = random.choice(facts)
    # Храним в нижнем регистре для сравнения
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
        # ИСПРАВЛЕНО: "city" вместо "сity"
        correct = game_state[uid]["city"]

        if text.lower() == correct:
            send(uid, "Правильно!")
        else:
            send(uid, f"Неверно! Это был: {correct.capitalize()}")

        game_state.pop(uid)
        return

    if mode == "quiz":
        correct = game_state[uid]["correct"]
        user_answer = text.lower().strip()

        # Проверяем разные варианты ответа
        if user_answer in ["правда", "истина", "да", "true"]:
            user_bool = "правда"
        elif user_answer in ["ложь", "неправда", "нет", "false"]:
            user_bool = "ложь"
        else:
            send(uid, "Пожалуйста, ответьте 'правда' или 'ложь'")
            return

        if user_bool == correct:
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

try:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = (event.text or "").strip().lower()

            print(f"Получено сообщение от {uid}: '{text}'")  # Для отладки

            if uid in game_state:
                process_game(uid, text)
                continue

            if text == "игры":
                send(
                    uid, "Выбери игру:\n"
                    "1 - Угадай число\n"
                    "2 - Угадай город по фотографии\n"
                    "3 - Правда или ложь")
                continue

            if text in commands and callable(commands[text]):
                commands[text](uid)
                continue

            send(uid, "Я тебя не понял. Напиши: игры")

except KeyboardInterrupt:
    print("\nБот остановлен")
except Exception as e:
    print(f"Ошибка: {e}")
    print("Перезапуск через 5 секунд...")
    import time
    time.sleep(5)
    # Здесь можно добавить перезапуск
