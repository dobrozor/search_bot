import telebot
from telebot.types import Message
import requests
from urllib.parse import quote
import urllib.parse
import time
from pprint import pprint

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = 'TOKEN_TG_BOT'
bot = telebot.TeleBot(TOKEN)


def get_file_url(file_id: str) -> str:
    """Получает прямую ссылку на файл по его file_id"""
    file_info = bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"


def generate_lens_url(image_url):
    """Генерирует ссылку для Google Lens"""
    encoded_url = urllib.parse.quote(image_url, safe='')
    current_time_ms = int(time.time() * 1000)
    lens_url = (
        f"https://lens.google.com/uploadbyurl?url={encoded_url}"
        f"&hl=ru&st={current_time_ms}&ep=gisbubu&vpw=978&vph=919"
    )
    return lens_url


def get_yandex_search_url(input_url):
    """Получает ссылку для поиска в Яндексе"""
    url = "https://yandex.ru/images-apphost/image-download"

    params = {
        "url": input_url,
        "cbird": "111",
        "images_avatars_size": "preview",
        "images_avatars_namespace": "images-cbir"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        cbir_id = data['cbir_id'].replace('/', '%2F')
        orig_url = quote(data['sizes']['orig']['path'], safe='')
        search_url = f"https://yandex.ru/images/search?cbir_id={cbir_id}&rpt=imageview&url={orig_url}"
        return search_url
    else:
        return None


@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    # Получаем фото с самым высоким разрешением (последний элемент в списке)
    photo = message.photo[-1]

    # Получаем информацию о файле
    file_url = get_file_url(photo.file_id)

    # Выводим информацию в консоль
    print("\n" + "=" * 50)
    print("Информация о полученном фото:")
    pprint({
        'file_id': photo.file_id,
        'width': photo.width,
        'height': photo.height,
        'file_size': photo.file_size,
        'file_url': file_url
    }, width=50)

    # Генерируем ссылки для Google Lens и Яндекс
    lens_url = generate_lens_url(file_url)
    yandex_search_url = get_yandex_search_url(file_url)

    message1 = f"🔎 По фотке инфа:\n\n[🇺🇸 Гугл фото]({lens_url})\n[🇷🇺 Яндекс фото]({yandex_search_url})"

    bot.reply_to(message, message1, parse_mode="MarkdownV2")


if __name__ == '__main__':
    print("Бот запущен. Ожидаю фото...")
    bot.infinity_polling()
