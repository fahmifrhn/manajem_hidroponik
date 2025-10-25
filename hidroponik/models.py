# hidroponik/models.py

from django.db import models
from django.utils import timezone

class Tanaman(models.Model):
    # Pilihan untuk dropdown jenis tanaman
    PLANT_CHOICES = [
        ('Bayam', 'Bayam'), ('Cabai', 'Cabai'), ('Caisim', 'Caisim'),
        ('Daun Bawang', 'Daun Bawang'), ('Kale', 'Kale'), ('Kangkung', 'Kangkung'),
        ('Pakcoy', 'Pakcoy'), ('Selada Air', 'Selada Air'), ('Seledri', 'Seledri'),
        ('Stroberi', 'Stroberi'), ('Timun', 'Timun'), ('Tomat', 'Tomat'),
    ]

    # Pilihan untuk status tanaman
    STATUS_CHOICES = (
        ('Bibit', 'Bibit'),
        ('Vegetatif', 'Vegetatif'),
        ('Berbunga', 'Berbunga/Berbuah'),
        ('Panen', 'Panen'),
    )
    # Informasi Dasar
    jenis_tanaman = models.CharField(max_length=50, choices=PLANT_CHOICES)
    varietas = models.CharField(max_length=100, blank=True, null=True, default="Tanpa Varietas")
    tanggal_tanam = models.DateField()
    media_tanam = models.CharField(max_length=100, blank=True)
    posisi = models.CharField(max_length=100, blank=True, verbose_name="Posisi Rak/Tandon")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Bibit')

    # Kebutuhan Nutrisi
    target_ppm = models.PositiveIntegerField(blank=True, null=True)
    target_ph = models.FloatField(blank=True, null=True, verbose_name="Target pH Ideal")
    target_suhu = models.FloatField(blank=True, null=True, verbose_name="Target Suhu (°C)")
    
    # Field lama yang masih relevan
    tanggal_panen_estimasi = models.DateField(blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Catatan")
    
    # FIELD BARU
    UNIT_CHOICES = [
        ('gram', 'gram'),
        ('kg', 'kg'),
    ]
    jumlah_hasil_angka = models.FloatField(blank=True, null=True, verbose_name="Jumlah Hasil")
    satuan_hasil = models.CharField(max_length=5, choices=UNIT_CHOICES, default='gram', blank=True)
    catatan_panen = models.TextField(blank=True, verbose_name="Catatan Panen")
    
    def __str__(self):
        return f"{self.get_jenis_tanaman_display()} - {self.varietas}"

class DataSensor(models.Model):
    tanaman = models.ForeignKey(Tanaman, on_delete=models.CASCADE, related_name='data_sensor')
    waktu_pencatatan = models.DateTimeField(default=timezone.now)
    ph = models.FloatField(verbose_name="pH Air")
    suhu = models.FloatField(verbose_name="Suhu Air (°C)") # Ubah nama field agar konsisten
    nutrisi_ppm = models.PositiveIntegerField(verbose_name="Tingkat Nutrisi (PPM)") # Ubah nama field
    ketinggian_air = models.FloatField(verbose_name="Ketinggian Air (cm)", null=True, blank=True) # Field baru
    
    def __str__(self):
        return f"Data untuk {self.tanaman.nama} pada {self.waktu_pencatatan.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-waktu_pencatatan']
    
 # MODEL BARU UNTUK PUPUK & NUTRISI
class PupukNutrisi(models.Model):
    UNIT_CHOICES = [
        ('ml', 'ml'),
        ('L', 'L'),
        ('gram', 'gram'),
        ('kg', 'kg'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Pupuk/Nutrisi")
    pabrikan = models.CharField(max_length=100, blank=True)
    jumlah = models.FloatField(verbose_name="Jumlah")
    satuan = models.CharField(max_length=5, choices=UNIT_CHOICES, default='ml')
    deskripsi = models.TextField(blank=True)
    tanggal_ditambahkan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama   
        
# MODEL BARU untuk Log Aktivitas
class LogAktivitas(models.Model):
    ACTIVITY_CHOICES = [
        ('Ganti Air', 'Ganti Air'),
        ('Tambah Nutrisi', 'Tambah Nutrisi'),
        ('Semprot Hama', 'Semprot Hama'),
        ('Pindah Tanaman', 'Pindah Tanaman'),
    ]
    tanaman = models.ForeignKey(Tanaman, on_delete=models.CASCADE, related_name='log_aktivitas')
    tanggal = models.DateTimeField(default=timezone.now)
    jenis_aktivitas = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    catatan = models.TextField()
    pupuk_yang_digunakan = models.ForeignKey(PupukNutrisi, on_delete=models.SET_NULL, null=True, blank=True)
    jumlah_yang_digunakan = models.FloatField(null=True, blank=True, help_text="Jumlah pupuk/nutrisi yang digunakan (sesuai satuan di stok)")
    class Meta:
        ordering = ['-tanggal']

            
    # MODEL BARU UNTUK INVENTARIS
class InventarisItem(models.Model):
    CATEGORY_CHOICES = [
        ('Peralatan', 'Peralatan'),
        ('Media Tanam', 'Media Tanam'),
        ('Lainnya', 'Lainnya'),
    ]

    nama_barang = models.CharField(max_length=200, verbose_name="Nama Barang")
    jumlah = models.PositiveIntegerField(blank=True, null=True)
    kategori = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Lainnya')
    catatan = models.TextField(blank=True)
    tanggal_ditambahkan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_barang
    
# MODEL BARU UNTUK DATA REFERENSI TANAMAN
class ProfilTanaman(models.Model):
    nama = models.CharField(max_length=100, unique=True, help_text="Nama harus sama dengan pilihan di Jenis Tanaman")
    estimasi_panen_hari = models.PositiveIntegerField()
    ph_ideal_min = models.FloatField()
    ph_ideal_max = models.FloatField()
    ppm_ideal_min = models.PositiveIntegerField()
    ppm_ideal_max = models.PositiveIntegerField()

    def __str__(self):
        return self.nama
    
class PengaturanTelegram(models.Model):
    bot_token = models.CharField(max_length=100, help_text="Token API dari BotFather Telegram")
    chat_id = models.CharField(max_length=50, help_text="Chat ID pengguna atau grup Telegram")

    def __str__(self):
        return "Pengaturan Notifikasi Telegram"