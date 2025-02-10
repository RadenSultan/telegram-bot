import asyncio
import logging
from datetime import datetime, timedelta

async def set_reminder(bot, chat_id, reminder_time, reminder_message):
    """
    Fungsi untuk mengatur pengingat di Telegram.
    
    Parameters:
    - bot: Instance dari Bot Telegram.
    - chat_id: ID chat pengguna.
    - reminder_time: Waktu pengingat dalam format datetime.
    - reminder_message: Pesan yang akan dikirim saat pengingat aktif.
    """
    try:
        now = datetime.now()
        time_difference = (reminder_time - now).total_seconds()
        
        if time_difference > 0:
            logging.info(f"Pengingat akan dikirim dalam {time_difference} detik.")
            await asyncio.sleep(time_difference)
            await bot.send_message(chat_id, f"⏰ Pengingat: {reminder_message}")
        else:
            logging.warning("Waktu pengingat sudah lewat. Pengingat tidak diatur.")
    except Exception as e:
        logging.error(f"Error saat mengatur pengingat: {e}")
