# Telegram-бот
## Информация о проекте
Telegram-бот с функциями перевода голосовых сообщений в текстовые и обработки фотографий

### Функция приветствия и краткая информация о работе бота
Все функции общения с telegram происходят через знак @
```
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет ✌️,' + message.chat.first_name
                     + '\n\nЭто бот для перевода голосовых сообщений в текст и обработки фотографий. '
                       '\n\nДля начала работы отправьте голосовое или фото')
```

### Функция для скачивания файла
Функция скачивает файл с сервера Telegram, генерирует имя, которое не вызовет ошибок при дальнейшей работе и 
сохраняет его в папке проекта
```
def download_file(my_bot, file_id):
    file_info = my_bot.get_file(file_id)
    downloaded_file = my_bot.download_file(file_info.file_path)
    filename = (file_id + file_info.file_path).replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename        
```
### Функция для форматирования файлов
Функция форматирует исходный telegram-файл с расширением ".oga" в файл с расширением ".wav", который подходит для 
дальнейшей работы. Для работы данной функции нужно скачать программу ffmpeg и прописать путь до исполняемого файла
```
    def oga2wav(files):
    command = ['/opt/homebrew/bin/ffmpeg', '-i', files, './out.wav']  # для работы бота нужно скачать программу ffmpeg
    # и прописать путь до исполняемого файла
    subprocess.run(command)
    wav_filename = 'out.wav'
    return wav_filename
```
### Функция для распознавания речи
Функция передает исходный .oga-файл в функцию oga2wav для форматирования в .wav, который уже может распознаваться с 
помощью модуля Google Speech Recognition, после распознавания мы получаем строку, далее мы удаляем .oga и .wav файлы 
из папки проекта
```
def recognize_speech(oga_filename):
    wav_filename = oga2wav(oga_filename)

    # Создаем экземпляр класса Recognizer
    r = sr.Recognizer()

    # Загружаем WAV-файл
    with sr.WavFile(wav_filename) as source:
        audio = r.listen(source)

    # Распознаем речь с помощью Google Speech Recognition
    text = r.recognize_google(audio, language='ru')

    # Сразу же удаляем телеграмм-файл ".oga" и сконвертированный ".wav"
    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text
```
### Функция для отправки полученного текста из голосового сообщения 
```    
@bot.message_handler(content_types=['voice'])
def transcript(message):
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)
```
### Функция для обработки полученных фотографий
Данная функция обрабатывает фото от пользователя посредством библиотеки PIL: в нашем случае идет 
увеличение контрастности, можно выбрать любые другие методы обработки из библиотеки
```
def transform_image(filename):
    source_image = Image.open(filename)
    enhanced_image = ImageEnhance.Contrast(source_image).enhance(1.4)
    enhanced_image = enhanced_image.convert('RGB')
    enhanced_image.save(filename)
    return filename
```
## Функция для скачивания, обработки и отправки фото пользователю
фото скачивается и передается в функцию transform_image для обработки, далее отправляется пользователю, после чего 
удаляется из каталога проекта
```
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
```

## Запуск бота
```
bot.polling()
```