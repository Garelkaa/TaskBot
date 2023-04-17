from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher.filters import Text
import cfg
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import Database
import keyboard
import random
from aiogram.types.message import ContentType

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('database.db')

class FSMAdd(StatesGroup):
    name = State()
    desc = State()

class FSMTask(StatesGroup):
    img = State()
    user_id = State()
    number = State()
    desc = State()
    done = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not db.user_exists(message.from_user.id):
        start_command = message.text
        referrer_id = str(start_command[7:])
        if str(referrer_id) != "":
            if str(referrer_id) != str(message.from_user.id):
                db.add_user(message.from_user.id, referrer_id)
                try:
                    await bot.send_message(referrer_id, "По вашей ссылке авторизовался новый пользователь!")
                except:
                    pass
            else:
                await bot.send_message(message.from_user.id, "Вы авторизовались по ссылке")
        else:
            db.add_user(message.from_user.id)
            await bot.send_message(message.from_user.id, f"Приветствуем в боте")
            await bot.send_message(message.from_user.id, "Выбирайте кнопку для перемещения", reply_markup=keyboard.main)


@dp.message_handler(Text("Задания"))
async def gettask(message: types.Message):
    if db.check_upgrade(message.from_user.id):
        await db.get_task_full(message)
    else:
        await db.get_task(message)
    await bot.send_message(message.from_user.id, f"Вот активные задания на сегодня", reply_markup=keyboard.menuTask)


@dp.message_handler(Text("Правила"))
async def pravila(message: types.Message):
    await bot.send_message(message.from_user.id, f"Если повторно купите абгрейд - деньги не возвращаем. И другие правила.")


@dp.message_handler(Text("Профиль"))
async def prof(message: types.Message):
    if db.check_upgrade(message.from_user.id):
        await bot.send_message(message.from_user.id, f"Ваш ID: {message.from_user.id}\nКоличество рефералов: {db.countRef(message.from_user.id)}\nКоличество доступных задания для профиля: Неограничено")
    else:
        await bot.send_message(message.from_user.id, f"Ваш ID: {message.from_user.id}\nКоличество рефералов: {db.countRef(message.from_user.id)}\nКоличество доступных задания для профиля: 3\nДоступен абгрейд!", reply_markup=keyboard.subInline)


@dp.message_handler(Text("Главная"))
async def goMain(message: types.Message):
    await bot.send_message(message.from_user.id, f"Вы на главной", reply_markup=keyboard.main)


@dp.message_handler(Text("Сдать задание"), state=None)
async def Submit(message: types.Message):
    await FSMTask.img.set()
    await bot.send_message(message.from_user.id, f"Отправьте фото-пруф к своему заданию.")


@dp.message_handler(content_types=['photo'], state=FSMTask.img)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMTask.next()
    await message.reply("Введите свой айди. Узнать можно в профиле")


@dp.message_handler(state=FSMTask.user_id)
async def load_userId(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.text
    await FSMTask.next()
    await message.reply(f"Уведите номер задания и любое число после. Пример: 1, 234.")


@dp.message_handler(state=FSMTask.number)
async def load_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = random.randint(0, 3333333)
    await FSMTask.next()
    await message.reply("Введите описание задание которое Вы выполнили.")


@dp.message_handler(state=FSMTask.desc)
async def load_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text

    await FSMTask.next()
    await message.reply(f"Теперь пройдите проверку на бота\nВведите число 128")


@dp.message_handler(state=FSMTask.done)
async def load_done(message: types.Message, state: FSMContext):
    if message.text >= '128':
        await message.reply(f"Вы не прошли проверку. Чтобы отправить выполненое задание пройдите форму заново!!!")
        await state.finish()
    else:
        async with state.proxy() as data:
            data['done'] = 0
        await message.reply(f"Ваше задание отправлено на модерацию. Если его примут Вы получите вознагрождение.")
        await db.addDonetask(state)
        await state.finish()
        adm = 626452615
        await bot.send_message(adm, f"Пользователь выполнил задание, введите 'Готово'")


@dp.message_handler(Text("Готово"))
async def admDoneTask(message: types.Message):
    if db.check_adm(message.from_user.id):
        await db.get_task_adm(message)


@dp.message_handler(commands=["done"])
async def doneAdm(message: types.Message):
    if db.check_adm(message.from_user.id):
        args = message.text.split()
        db.done(args[1], args[2])
        await bot.send_message(message.from_user.id, text=f"✅ Вы изменили параметр done.\nID » {args[1]}\n Додано » {args[2]}", reply_markup=keyboard.main)


@dp.message_handler(commands=["Очистить"])
async def cleartask(message: types.Message):
    if db.check_adm(message.from_user.id):
        db.clearTask()
        await bot.send_message(message.from_user.id, f"Очищено")


@dp.callback_query_handler(text="upgrade")
async def subactivate(call: types.CallbackQuery):
    # if db.check_upgrade(message.from_user.id):
    #     await bot.send_message(message.from_user.id, f"У вас уже прокачан аккаунт")
    # else:
    await bot.send_invoice(chat_id=call.from_user.id, title="Улучшение аккаунта", description='После оплаты вы получите доступ к неограниченным количетвам заданий.', payload="upgrade", provider_token=cfg.KASSA, currency="RUB", start_parameter="Upgrade", prices=[{"label": "Руб", "amount": 100000}])


@dp.pre_checkout_query_handler()
async def process_pay(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def oplataqweqwe(message: types.Message):
    if message.successful_payment.invoice_payload == 'upgrade':
        if db.check_upgrade(message.from_user.id):
            await bot.send_message(message.from_user.id, f"У вас уже прокачан аккаунт. 1 правило нашего бота - читать условия. Деньги возвращены не будут!")
        else:
            await bot.send_message(message.from_user.id, f"Оплата прошла успешно!\nВы прокачали свой аккаунт")
            db.set_upgrade(message.from_user.id, +1)

@dp.message_handler(Text("Добавить задание"), state=None)
async def addtask(message: types.Message): 
    if db.check_adm(message.from_user.id):
        await FSMAdd.name.set()
        await bot.send_message(message.from_user.id, f"Введите название задания")


@dp.message_handler(state=FSMAdd.name)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdd.next()
    await message.reply("Введите описание задания")


@dp.message_handler(state=FSMAdd.desc)
async def load_userId(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.reply("Успешно")
    await db.addtask(state)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
