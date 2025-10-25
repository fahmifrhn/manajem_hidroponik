# hidroponik/admin.py
from django.contrib import admin
from .models import Tanaman, DataSensor, LogAktivitas
from .models import PupukNutrisi
from .models import InventarisItem
from .models import ProfilTanaman

admin.site.register(PupukNutrisi)
admin.site.register(InventarisItem)
admin.site.register(ProfilTanaman)

class DataSensorInline(admin.TabularInline):
    model = DataSensor
    extra = 1 # Tampilkan 1 form kosong untuk data baru

@admin.register(Tanaman)
class TanamanAdmin(admin.ModelAdmin):
    # Ganti baris di bawah ini
    list_display = ('jenis_tanaman', 'varietas', 'tanggal_tanam', 'status')
    list_filter = ('status', 'jenis_tanaman') # Tambahkan filter agar lebih mudah
    inlines = [DataSensorInline]

@admin.register(DataSensor)
class DataSensorAdmin(admin.ModelAdmin):
    list_display = ('tanaman', 'waktu_pencatatan', 'ph', 'nutrisi_ppm', 'suhu')
    list_filter = ('tanaman', 'waktu_pencatatan')