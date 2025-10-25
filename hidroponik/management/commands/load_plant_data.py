# hidroponik/management/commands/load_plant_data.py
import pandas as pd
from django.core.management.base import BaseCommand
from hidroponik.models import ProfilTanaman

class Command(BaseCommand):
    help = 'Memuat data profil tanaman dari file CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path menuju file CSV')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']
        self.stdout.write(f"Membaca file dari: {file_path}")

        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File tidak ditemukan di path: {file_path}"))
            return

        for index, row in df.iterrows():
            # ---- BLOK TRY-EXCEPT UNTUK MENANGANI ERROR PER BARIS ----
            try:
                if pd.isna(row['Nama Tanaman']):
                    continue

                # Proses rentang pH
                ph_str = str(row['pH Ideal']).replace(',', '.') # Ganti koma dengan titik
                ph_range = ph_str.split('-')
                ph_min = float(ph_range[0])
                ph_max = float(ph_range[-1])
                
                # Proses rentang PPM
                ppm_str = str(row['PPM Ideal (nutrisi)'])
                ppm_str_cleaned = ppm_str.replace('.', '') # Hapus titik ribuan
                ppm_range = ppm_str_cleaned.split('-')
                
                ppm_min = int(ppm_range[0])
                ppm_max = int(ppm_range[-1])
                
                profil, created = ProfilTanaman.objects.update_or_create(
                    nama=row['Nama Tanaman'],
                    defaults={
                        'estimasi_panen_hari': int(row['Estimasi Panen (hari)']),
                        'ph_ideal_min': ph_min,
                        'ph_ideal_max': ph_max,
                        'ppm_ideal_min': ppm_min,
                        'ppm_ideal_max': ppm_max,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Membuat profil untuk: {row['Nama Tanaman']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Memperbarui profil untuk: {row['Nama Tanaman']}"))
            
            except Exception as e:
                # Jika ada error di baris manapun, cetak peringatan dan lanjut ke baris berikutnya
                self.stdout.write(self.style.ERROR(f"Gagal memproses baris {index + 2} untuk tanaman '{row['Nama Tanaman']}'. Error: {e}"))
                continue
        
        self.stdout.write(self.style.SUCCESS("Selesai memuat data."))