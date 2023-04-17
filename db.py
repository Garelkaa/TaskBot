import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import cfg
from aiogram import Bot
bot = Bot(token=cfg.TOKEN)


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM users WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, ref_id=None):
        with self.connection:
            if ref_id != None:
                return self.cursor.execute("INSERT INTO 'users' ('user_id', 'ref_id') VALUES (?, ?)", (user_id, ref_id,))
            else:
                return self.cursor.execute("INSERT INTO users (`user_id`) VALUES (?)", (user_id,))

    async def addtask(self, state: FSMContext):
        with self.connection:
            async with state.proxy() as data:
                self.cursor.execute(
                    "INSERT INTO Task VALUES (?, ?)", tuple(data.values()))

    def countRef(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(`user_id`) as count FROM `users` WHERE `ref_id` = ?", (user_id,)).fetchone()[0]

    def user_referal(self, user_id,):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `ref_id` FROM users WHERE `user_id` = ?", (user_id,)).fetchmany(1)
            return int(result[0][0]) if result else None

    async def addDonetask(self, state: FSMContext):
        with self.connection:
            async with state.proxy() as data:
                self.cursor.execute(
                    "INSERT INTO STask VALUES (?, ?, ?, ?, ?)", tuple(data.values()))

    async def get_task(self, message):
        with self.connection:
            for ret in self.cursor.execute("SELECT * FROM Task LIMIT 3").fetchall():
                await bot.send_message(message.from_user.id, f"Задание: {ret[0]}\nОписание задания: {ret[1]}")

    async def get_task_full(self, message):
        with self.connection:
            for ret in self.cursor.execute("SELECT * FROM Task").fetchall():
                await bot.send_message(message.from_user.id, f"Задание: {ret[0]}\nОписание задания: {ret[1]}")

    async def get_task_adm(self, message):
        with self.connection:
            for ret in self.cursor.execute("SELECT * FROM STask WHERE `done` = 0").fetchall():
                await bot.send_photo(message.from_user.id, ret[0])
                await bot.send_message(message.from_user.id, f"ID user: {ret[2]}\nАйди заявки: {ret[1]}\nОписание сделаного задания: {ret[3]}\nГотовность: {ret[4]}\n /done {ret[2]} 🟢  🔴 🟡")

    def check_upgrade(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                f"SELECT `upgrade` FROM users WHERE `user_id` = ?", (user_id,)).fetchall()
            return result[0][0]

    def check_adm(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                f"SELECT `adm` FROM users WHERE `user_id` = ?", (user_id,)).fetchall()
            return result[0][0]

    def done(self, user_id, done):
        with self.connection:
            self.cursor.execute(
                "UPDATE STask SET `done` = done + ? WHERE `id` = ?", (done, user_id,))

    def clearTask(self):
        with self.connection:
            self.cursor.execute("DELETE FROM Task").fetchall()

    def set_upgrade(self, user_id, upgrade):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET `upgrade` = upgrade + ? WHERE `user_id` = ?", (upgrade, user_id,))
