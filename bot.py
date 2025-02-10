import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode  # Diperbaiki di sini
import asyncio
from datetime import datetime, timedelta
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton

from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# Pastikan set_reminder ada di reminder.py dan diimport di file ini
from reminder import set_reminder


# Pastikan path sesuai dengan lokasi file .env
env_path = r"D:\Coding\telegram-bot\.env"
load_dotenv(dotenv_path=r"D:\Coding\telegram-bot\.env")

TOKEN = os.getenv("TOKEN")  # Ambil token dengan benar
if not TOKEN:
    raise ValueError("TOKEN tidak ditemukan di .env. Pastikan file .env sudah diisi dengan benar.")

DOWNLOAD_DIR = "downloads"

# Inisialisasi bot dan dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# Pastikan folder download tersedia
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

from datetime import datetime, timedelta

@dp.message_handler(commands=['reminder'])
async def set_reminder_command(message: types.Message):
    """Handler untuk mengatur pengingat."""
    try:
        # Format: /reminder HH:MM Pesan pengingat
        args = message.text.split(" ", 2)
        
        # Cek jika format input kurang dari yang diharapkan
        if len(args) < 3:
            await message.reply("Format perintah salah. Gunakan: /reminder HH:MM Pesan pengingat.")
            return
        
        reminder_time_str = args[1]  # Waktu pengingat dari input
        reminder_message = args[2]   # Pesan pengingat dari input

        # Parse waktu pengingat dari string
        try:
            reminder_time = datetime.strptime(reminder_time_str, "%H:%M")
        except ValueError:
            await message.reply("Waktu yang dimasukkan tidak valid. Gunakan format HH:MM (misalnya 15:30).")
            return

        # Set tanggal pengingat berdasarkan hari ini
        reminder_time = reminder_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        # Jika waktu pengingat sudah lewat, set untuk hari berikutnya
        if reminder_time < datetime.now():
            reminder_time += timedelta(days=1)

        # Set pengingat menggunakan fungsi set_reminder
        await set_reminder(bot, message.chat.id, reminder_time, reminder_message)
        
        # Memberikan konfirmasi kepada pengguna
        await message.reply(f"Pengingat telah diatur untuk {reminder_time.strftime('%H:%M')} dengan pesan: {reminder_message}")
    
    except Exception as e:
        # Tangani jika ada error
        print(f"Error pengingat: {e}")
        await message.reply("Terjadi kesalahan saat mengatur pengingat.")


        
async def main():
    await dp.start_polling(bot)

import os
from yt_dlp import YoutubeDL

def download_video(url, resolution=None):
    """Fungsi untuk mendownload video dengan format terbaik yang tersedia."""

    # Pilih format yang benar-benar tersedia, bukan selalu 137+140
    video_format = 'bv*[vcodec^=avc1]+ba[ext=m4a]/b[ext=mp4]'

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': video_format,
        'merge_output_format': 'mp4',
        'postprocessors': [
    {'key': 'FFmpegMerger'},
    {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
    {'key': 'FFmpegMetadata'},
    {'key': 'FFmpegEmbedSubtitle'}
],

        'noplaylist': True,
        'force_overwrites': True,
        'rm_cachedir': True,
        'ignoreerrors': True,
        'verbose': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"🔄 Mengunduh video dari: {url}")
            ydl.download([url])

        # Cari file MP4 hasil akhir
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        mp4_files = [f for f in downloaded_files if f.endswith('.mp4')]

        if mp4_files:
            latest_file = max(mp4_files, key=lambda f: os.path.getctime(os.path.join(DOWNLOAD_DIR, f)))
            mp4_filename = os.path.join(DOWNLOAD_DIR, latest_file)

            # Cek apakah file MP4 benar-benar ada
            if os.path.exists(mp4_filename):
                print(f"✅ Video berhasil diunduh: {mp4_filename}")
                return mp4_filename
            else:
                print(f"❌ File MP4 hasil penggabungan tidak ditemukan: {mp4_filename}")
                return None

    except FileNotFoundError:
        print("⚠️ File video/audio tidak ditemukan. Coba gunakan format lain.")
        return None
    except Exception as e:
        print(f"⚠️ Error saat mendownload video: {e}")
        return None


def download_music(url):
    """Fungsi untuk mendownload musik dari link apapun."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info).replace(".webm", ".mp3")
    except Exception as e:
        print(f"Error saat mendownload musik: {e}")
        return None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):

    # Gambar untuk menyambut pengguna
    welcome_photo_path = r'D:\Coding\welcome.jpg' # Ganti dengan path yang diinginkan

    # Ambil nama depan pengguna
    user_name = message.from_user.first_name

    # Kirim gambar dan teks sambutan
    await bot.send_photo(
        message.chat.id,
        photo=open(welcome_photo_path, 'rb'), # Membuka gambar
        caption=f"⚡Halo {user_name}! Gunakan perintah berikut ini:\n\n"
        "/video (link) - Untuk mendownload Video 🎬\n\n"
        "/music (link) - Untuk mendownload Musik 🎵"
    )

@dp.message_handler(commands=['video'])
async def handle_video(message: types.Message):
    """Handler untuk mendownload video."""
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("Mohon berikan link video setelah perintah /video.")
        return
    
    url = args[1].strip()
    if "youtube.com" in url or "youtu.be" in url:
        keyboard = InlineKeyboardMarkup()
        resolutions = ["144", "240", "360", "480", "720", "1080"]
        for res in resolutions:
            keyboard.add(InlineKeyboardButton(text=f"{res}p", callback_data=f"yt_{res}_{url}"))
        await message.reply("Pilih resolusi video:", reply_markup=keyboard)
    else:
        await message.reply("Mengunduh video... Mohon tunggu!")
        filename = download_video(url)
        if filename:
            await bot.send_video(message.chat.id, InputFile(filename))
            os.remove(filename)

            # Menetapkan waktu pengingat 5 menit setelah video selesai diunduh
            reminder_time = datetime.now() + timedelta(minutes=5) # Set pengingat 5 menit setelah selesai
            reminder_message = "Tonton video yang baru saja kamu unduh !"

            # Set Pengingat
            await set_reminder(bot, message.chat.id, reminder_time, reminder_message)
            await message.reply(f"Pengingat telah diatur untuk {reminder_time.strftime('%H:%M')} dengan pesan :{reminder_message}")
        else:
            await message.reply("Gagal mengunduh video.")

@dp.message_handler(commands=['music'])
async def handle_music(message: types.Message):
    """Handler untuk mendownload musik."""
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("Mohon berikan link musik setelah perintah /music.")
        return
    
    url = args[1].strip()
    await message.reply("Mengunduh audio... Mohon tunggu!")
    filename = download_music(url)
    if filename:
        await bot.send_audio(message.chat.id, InputFile(filename))
        os.remove(filename)
    else:
        await message.reply("Gagal mengunduh musik.")

@dp.callback_query_handler(lambda c: c.data.startswith("yt_"))
async def process_youtube_download(callback_query: types.CallbackQuery):
    """Handler untuk memproses download video YouTube dengan resolusi tertentu."""
    _, res, url = callback_query.data.split("_", 2)
    await bot.send_message(callback_query.from_user.id, f"Mengunduh video YouTube dalam {res}p...")
    filename = download_video(url, res)
    if filename:
        await bot.send_video(callback_query.from_user.id, InputFile(filename))
        os.remove(filename)
    else:
        await bot.send_message(callback_query.from_user.id, "Gagal mengunduh video.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
