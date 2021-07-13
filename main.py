import telebot
from telebot import types
import cv2
import numpy
from mss import mss
from PIL import Image
import time

bot = telebot.TeleBot('1733207219:AAF3oEXRf1ThvQCnVd2SHXdeqx9eWPwMpkw')
message_id = 0
started = False
profile = 'PC'
lines = ''
coords = [0,0,0,0]
inied = False
standard=0
pic_send=False

def ini():
    try:
        open('profiles.txt','x')
        bot.send_message(message_id,'Profiles not found')
    except:
        file = open('profiles.txt','r')
        file_text = file.read()
        global lines
        lines = file_text.split('\n')

        global standard
        standard = cv2.imread('your_file.jpeg')
        grayImage = cv2.cvtColor(standard, cv2.COLOR_BGR2GRAY)
        (thresh, standard) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
        global inied
        inied = True

def start():
    global rest
    global pic_send
    if(started):
        picture_main = video_capture()
        picture = crop_picture(picture_main)
        picture = color_picture(picture)
        count = eqcount(picture, standard)
        # print(count)
        if(count > 40000):
            if(pic_send == False):
                picture=crop_picture_big(picture_main)
                picture= cv2.cvtColor(picture,cv2.COLOR_BGR2RGB)
                im = Image.fromarray(picture)
                im.save("send.jpeg")
                bot.send_photo(message_id,photo=open('send.jpeg','rb'))
                pic_send = True
        else:
            pic_send = False
        if(pic_send == False):
            time.sleep(5)
            start()
        else:
            time.sleep(25)
            bot.send_message(message_id, '10 seconds left')
        # im = Image.fromarray(picture)
        # im.save("your_file.jpeg")
        # show_picture(picture)

def eqcount(picture,standard):
    count = 0
    for i in range(len(picture)):
        for j in range(len(picture[i])):
            if picture[i][j] == standard[i][j]:
                count += 1
    return count

def video_capture():
    mon = {'top': 1, 'left': 1, 'width': 1919, 'height': 1079}
    with mss() as sct:
        img = sct.grab(mon)
        img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def show_picture(picture):
    cv2.imshow('Picture', picture)
    cv2.waitKey(0)

def crop_picture(picture):
    global coords
    picture = picture[coords[0]:coords[1], coords[2]:coords[3]]
    return picture

def crop_picture_big(picture):
    global coords
    picture = picture[coords[0]-430:coords[1], coords[2]:coords[3]]
    return picture

def color_picture(picture):
    hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)
    h_min = numpy.array((0, 0, 23), numpy.uint8)
    h_max = numpy.array((0, 9, 128), numpy.uint8)
    picture = cv2.inRange(hsv, h_min, h_max)
    return picture

def color_picture2(picture):
    hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)
    h_min = numpy.array((0, 0, 0), numpy.uint8)
    h_max = numpy.array((255, 255, 255), numpy.uint8)
    picture = cv2.inRange(hsv, h_min, h_max)
    return picture


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global started
    if message.text == '/ini':
        global message_id
        message_id = message.from_user.id
        ini()
        keys = []
        keyboard = types.InlineKeyboardMarkup();
        for line in lines:
            text = line.split('=')
            keys.append(types.InlineKeyboardButton(text=text[0], callback_data=text[0]))
        for key in keys:
            keyboard.add(key)
        bot.send_message(message.from_user.id, text='Chose profile', reply_markup=keyboard)
    if message.text == "/help":
        keyboard = types.InlineKeyboardMarkup();  # наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Все хорошо', callback_data='yes');  # кнопка «Да»
        keyboard.add(key_yes);  # добавляем кнопку в клавиатуру
        question = 'Что у тебя за проблема?';
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    if (inied):
        if message.text == '/start':
            started = True
            bot.send_message(message.from_user.id, 'Program is started')
            start()
        if message.text == '/stop':
            started = False
            bot.send_message(message.from_user.id, 'Program is stopped')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'OK');
    if (inied):
        for line in lines:
            text = line.split('=')
            if (call.data == text[0]):
                global coords
                coords_text = text[1].split('/')
                coords[0] = int(coords_text[0])
                coords[1] = int(coords_text[1])
                coords[2] = int(coords_text[2])
                coords[3] = int(coords_text[3])
                bot.send_message(call.message.chat.id, 'Profile "' + text[0] + '" is chosen')

bot.polling(none_stop=True, interval=0)
print("Bot is now ON")