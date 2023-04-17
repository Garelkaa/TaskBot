from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

mainBtn = [
    [
        KeyboardButton(text='Профиль'),
        KeyboardButton(text='Задания'),
        KeyboardButton(text='Правила')
    ],
    # [
    #     Key
    # ]
]

main = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=mainBtn)

menuTaskBtn = [
    [
        KeyboardButton(text='Сдать задание')
    ],
    [
        KeyboardButton(text='Главная')
    ]
]

menuTask = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=menuTaskBtn)


subInline = InlineKeyboardMarkup(row_width=1)

upgradeBtn = InlineKeyboardButton(
    text='Прокачать аккаунт', callback_data="upgrade")

subInline.insert(upgradeBtn)
