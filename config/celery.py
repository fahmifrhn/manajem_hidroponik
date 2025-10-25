# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Setel modul pengaturan default Django untuk program 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Menggunakan string di sini berarti worker tidak perlu
# men-serialisasi objek konfigurasi ke proses anak.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Muat modul tugas secara otomatis dari semua aplikasi Django yang terdaftar.
app.autodiscover_tasks()