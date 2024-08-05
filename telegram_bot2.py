# 1. Подключение библиотек
import telebot
import subprocess
import os
import speech_recognition as sr
from PIL import Image, ImageEnhance

token = 'ENTER_YOUR_TOKEN_HERE'  # введите токен от вашего телеграмм-бота
bot = telebot.TeleBot(token)


# 2. Функция, приветствия на команду /start.
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет ✌️,' + message.chat.first_name
                     + '\n\nЭто бот для перевода голосовых сообщений в текст и обработки фотографий. '
                       '\n\nДля начала работы отправьте голосовое или фото')


# 3. Скачивание файла, который прислал пользователь
def download_file(my_bot, file_id):
    file_info = my_bot.get_file(file_id)
    downloaded_file = my_bot.download_file(file_info.file_path)
    filename = (file_id + file_info.file_path).replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


# 4. Конвертировать исходное расширение голосового сообщения из telegram "".oga" в ".wav", которое читается функцией
def oga2wav(files):
    command = ['/opt/homebrew/bin/ffmpeg', '-i', files, './out.wav']  # для работы бота нужно скачать программу ffmpeg
    # и прописать путь до исполняемого файла
    subprocess.run(command)
    wav_filename = 'out.wav'
    return wav_filename


# 5. Перевод голоса в текст + удаление использованных файлов
def recognize_speech(oga_filename):
    wav_filename = oga2wav(oga_filename)

    # Создаем экземпляр класса Recognizer
    r = sr.Recognizer()

    # Загружаем WAV-файл
    with sr.WavFile(wav_filename) as source:
        audio = r.listen(source)

    # Распознаем речь с помощью Google Speech Recognition
    text = r.recognize_google(audio, language='ru')

    # Сразу же удаляем telegram-файл ".oga" и сконвертированный ".wav"
    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text


# 6. Функция, отправляющая текст в ответ на голосовое сообщение
@bot.message_handler(content_types=['voice'])
def transcript(message):
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)


# 7. Функция для обработки изображения
def transform_image(filename):
    source_image = Image.open(filename)
    enhanced_image = ImageEnhance.Contrast(source_image).enhance(1.4)
    enhanced_image = enhanced_image.convert('RGB')
    enhanced_image.save(filename)
    return filename


# 8. Функция для трансформации и отправки обработанного изображения пользователю
@bot.message_handler(content_types=['photo'])
def resend_photo(message):
    file_id = message.photo[-1].file_id
    filename = download_file(bot, file_id)

    transform_image(filename)

    image = open(filename, 'rb')
    bot.send_photo(message.chat.id, image)
    image.close()

    if os.path.exists(filename):
        os.remove(filename)


# 9. Запуск бота.
bot.polling()
