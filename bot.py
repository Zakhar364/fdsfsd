import asyncio
import os
from urllib.parse import quote
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

# Импортируем TOKEN из файла config.py
from config import TOKEN

class ImageAPI:
    async def download_image(self, prompt, save_path="generated_image.png"):
        """
        Асинхронное скачивание изображения.
        Добавлен обязательный параметр модели &flux для стабильной работы API.
        """
        # Кодируем текст и принудительно заставляем использовать рабочую модель Flux
        encoded_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/image/{encoded_prompt}?model=flux"
        
        print(f"[LOG] Отправка запроса к API: {url}")
        
        try:
            # Увеличиваем таймаут соединения, так как генерация Flux может занимать время
            timeout = aiohttp.ClientTimeout(total=40)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"[LOG] Ответ сервера Pollinations. Статус-код: {response.status}")
                    
                    if response.status == 200:
                        content = await response.read()
                        
                        # Проверяем, что нам прислали не пустой файл или не текстовую ошибку
                        if len(content) < 500:
                            print(f"[LOG] Ошибка: Сервер прислал слишком маленький файл (возможно, текст ошибки).")
                            return False
                            
                        with open(save_path, "wb") as f:
                            f.write(content)
                        print(f"[LOG] Файл успешно сохранен как: {save_path}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"[LOG] Ошибка сервера ({response.status}): {error_text}")
                        return False
        except Exception as e:
            print(f"[LOG] Исключение во время работы с сетью: {e}")
            return False

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
api = ImageAPI()

@dp.message(Command("start"))
async def start_handler(message: Message):
    """Приветственное сообщение."""
    await message.answer(
        "Привет! Напиши мне любой текст (промт на английском или русском), и я сгенерирую по нему картинку."
    )

@dp.message(F.text)
async def generate_handler(message: Message):
    """Обработка текстовых запросов для генерации."""
    prompt = message.text
    chat_id = message.chat.id
    filename = f"image_{chat_id}.png"
    
    # Отправляем промежуточный статус
    status_message = await message.answer("🔄 Генерирую изображение, подождите...")
    
    # Запускаем генерацию
    success = await api.download_image(prompt, filename)
    
    if success and os.path.exists(filename):
        try:
            # Удаляем плашку загрузки и отправляем фото
            await status_message.delete()
            photo = FSInputFile(filename)
            await message.answer_photo(photo=photo, caption=f"✨ Результат по запросу: {prompt}")
        except Exception as send_error:
            print(f"[LOG] Не удалось отправить фото в Телеграм: {send_error}")
            await message.answer("❌ Ошибка при отправке файла внутри Telegram.")
        finally:
            # Чистим за собой дисковое пространство
            if os.path.exists(filename):
                os.remove(filename)
    else:
        await status_message.edit_text("❌ Не удалось сгенерировать изображение. Попробуйте изменить запрос.")

async def main():
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



