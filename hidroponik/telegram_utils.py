# hidroponik/telegram_utils.py
import requests
from .models import PengaturanTelegram

def kirim_pesan_telegram(pesan):
    try:
        # Ambil pengaturan dari database
        pengaturan = PengaturanTelegram.objects.first()
        if not pengaturan or not pengaturan.bot_token or not pengaturan.chat_id:
            print("Pengaturan Telegram belum diisi.")
            return False

        token = pengaturan.bot_token
        chat_id = pengaturan.chat_id

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': pesan,
            'parse_mode': 'HTML' # Agar bisa menggunakan tag tebal, miring, dll.
        }

        response = requests.post(url, json=payload)
        return response.status_code == 200

    except Exception as e:
        print(f"Gagal mengirim pesan Telegram: {e}")
        return False