# hidroponik/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Tanaman, LogAktivitas
from .telegram_utils import kirim_pesan_telegram

@shared_task
def cek_dan_kirim_pengingat():
    print("Menjalankan tugas pengecekan pengingat...")
    tanaman_aktif = Tanaman.objects.exclude(status='Panen')
    batas_hari_ganti_air = 7

    for tanaman in tanaman_aktif:
        log_ganti_air_terakhir = tanaman.log_aktivitas.filter(jenis_aktivitas='Ganti Air').first()
        
        pesan_notifikasi = None
        
        if log_ganti_air_terakhir:
            hari_berlalu = (timezone.now() - log_ganti_air_terakhir.tanggal).days
            if hari_berlalu >= batas_hari_ganti_air:
                pesan_notifikasi = f"💧 <b>PENGINGAT</b>\n\nSudah <b>{hari_berlalu} hari</b> sejak terakhir ganti air untuk tanaman {tanaman}. Sebaiknya segera diperiksa."
        else:
            hari_sejak_tanam = (timezone.now().date() - tanaman.tanggal_tanam).days
            if hari_sejak_tanam >= batas_hari_ganti_air:
                pesan_notifikasi = f"💧 <b>PENGINGAT</b>\n\nTanaman {tanaman} sudah berumur <b>{hari_sejak_tanam} hari</b> dan belum pernah dicatat ganti air."

        if pesan_notifikasi:
            kirim_pesan_telegram(pesan_notifikasi)
            # --- BARIS INI YANG DIPERBAIKI ---
            print(f"Mengirim notifikasi untuk {tanaman}")
    
    return "Tugas pengecekan pengingat selesai."