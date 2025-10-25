# hidroponik/views.py
# hidroponik/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Avg, Count, Sum, F, Case, When, fields, ExpressionWrapper
from django.db.models.functions import TruncMonth
from datetime import timedelta
import datetime
import csv
from django.http import HttpResponse

# Impor semua model dan form
from .models import (
    Tanaman, DataSensor, LogAktivitas, PupukNutrisi, 
    InventarisItem, ProfilTanaman, PengaturanTelegram
)
from .forms import (
    TanamanForm, DataSensorForm, LogAktivitasForm, 
    PanenForm, PupukNutrisiForm, InventarisForm, PengaturanTelegramForm
)
# Impor fungsi pengirim pesan
from .telegram_utils import kirim_pesan_telegram

# hidroponik/views.py

def dashboard(request):
    # Pastikan semua baris ini rata kiri (dengan 4 spasi indentasi)
    hari_ini = timezone.now().date()
    tanaman_aktif = Tanaman.objects.exclude(status__in=['Panen', 'Dipanen'])
    siap_panen = tanaman_aktif.filter(tanggal_panen_estimasi__lte=hari_ini)
    
    jumlah_tanaman_aktif = tanaman_aktif.count()
    jumlah_siap_panen = siap_panen.count()

    aktivitas_terbaru = DataSensor.objects.all()[:5]

    context = {
        'jumlah_tanaman_aktif': jumlah_tanaman_aktif,
        'jumlah_siap_panen': jumlah_siap_panen,
        'aktivitas_terbaru': aktivitas_terbaru,
    }
    return render(request, 'hidroponik/dashboard.html', context)

    # Logika Data Statistik
    hari_ini = timezone.now().date()
    tanaman_aktif = Tanaman.objects.exclude(status__in=['Panen', 'Dipanen'])
    siap_panen = tanaman_aktif.filter(tanggal_panen_estimasi__lte=hari_ini)
    
    jumlah_tanaman_aktif = tanaman_aktif.count()
    jumlah_siap_panen = siap_panen.count()

    # Logika Aktivitas Terbaru
    aktivitas_terbaru = DataSensor.objects.all()[:5] # Ambil 5 data sensor terbaru

    context = {
        'sapaan': sapaan,
        'jumlah_tanaman_aktif': jumlah_tanaman_aktif,
        'jumlah_siap_panen': jumlah_siap_panen,
        'aktivitas_terbaru': aktivitas_terbaru,
    }
    return render(request, 'hidroponik/dashboard.html', context)

# Ganti fungsi detail_tanaman Anda dengan ini
def detail_tanaman(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    sensor_data = tanaman.data_sensor.all()
    activity_log = tanaman.log_aktivitas.all()

    sensor_form = DataSensorForm()
    activity_form = LogAktivitasForm()
    panen_form = PanenForm(instance=tanaman)

    if request.method == 'POST':
        if 'submit_sensor' in request.POST:
            form = DataSensorForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.tanaman = tanaman
                instance.save()
                messages.success(request, 'Data sensor berhasil disimpan!')

                # --- LOGIKA NOTIFIKASI 1 DIMULAI ---
                try:
                    profil = ProfilTanaman.objects.get(nama=tanaman.get_jenis_tanaman_display())

                    if not (profil.ph_ideal_min <= instance.ph <= profil.ph_ideal_max):
                        pesan = f"⚠️ <b>PERINGATAN pH</b>\n\nTanaman: {tanaman}\npH Saat Ini: <b>{instance.ph}</b>\nRentang Ideal: {profil.ph_ideal_min}-{profil.ph_ideal_max}"
                        kirim_pesan_telegram(pesan)

                    if not (profil.ppm_ideal_min <= instance.nutrisi_ppm <= profil.ppm_ideal_max):
                        pesan = f"📉 <b>PERINGATAN PPM</b>\n\nTanaman: {tanaman}\nPPM Saat Ini: <b>{instance.nutrisi_ppm}</b>\nRentang Ideal: {profil.ppm_ideal_min}-{profil.ppm_ideal_max}"
                        kirim_pesan_telegram(pesan)
                except ProfilTanaman.DoesNotExist:
                    pass
                # --- LOGIKA NOTIFIKASI 1 SELESAI ---

                return redirect('detail_tanaman', pk=tanaman.pk)

        elif 'submit_activity' in request.POST:
            form = LogAktivitasForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.tanaman = tanaman

                if instance.jenis_aktivitas == 'Tambah Nutrisi':
                    pupuk = instance.pupuk_yang_digunakan
                    jumlah = instance.jumlah_yang_digunakan

                    if pupuk and jumlah is not None:
                        pupuk.jumlah -= jumlah
                        pupuk.save()
                        messages.success(request, f'Log aktivitas berhasil disimpan. Stok {pupuk.nama} telah dikurangi.')
                    else:
                        messages.warning(request, 'Pilih pupuk dan jumlah untuk mengurangi stok.')
                else:
                     messages.success(request, 'Log aktivitas berhasil disimpan!')

                instance.save()
                return redirect('detail_tanaman', pk=tanaman.pk)

    context = {
        'tanaman': tanaman,
        'sensor_data': sensor_data,
        'activity_log': activity_log,
        'sensor_form': sensor_form,
        'activity_form': activity_form,
        'panen_form': panen_form,
    }
    return render(request, 'hidroponik/detail_tanaman.html', context)

def tambah_tanaman(request):
    if request.method == 'POST':
        form = TanamanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daftar_tanaman')
    else:
        form = TanamanForm()
    return render(request, 'hidroponik/form_generic.html', {'form': form, 'title': 'Tambah Tanaman Baru'})

def tambah_data_sensor(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    if request.method == 'POST':
        form = DataSensorForm(request.POST)
        if form.is_valid():
            data_sensor_baru = form.save(commit=False)
            data_sensor_baru.tanaman = tanaman
            data_sensor_baru.save()
            return redirect('detail_tanaman', pk=tanaman.pk)
    else:
        form = DataSensorForm()
    return render(request, 'hidroponik/form_generic.html', {'form': form, 'title': 'Tambah Tanaman Baru'})

def manajemen_tanaman(request):
    # Ambil semua tanaman yang belum dipanen
    semua_tanaman = Tanaman.objects.exclude(status='Dipanen').order_by('-tanggal_tanam')
    context = {
        'semua_tanaman': semua_tanaman
    }
    return render(request, 'hidroponik/manajemen_tanaman.html', context)

def hapus_tanaman(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    if request.method == 'POST':
        tanaman.delete()
        return redirect('manajemen_tanaman')
    # Jika bukan POST, redirect saja ke halaman manajemen
    return redirect('manajemen_tanaman')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="daftar_tanaman.csv"'

    writer = csv.writer(response)
    # Tulis header
    writer.writerow(['Jenis Tanaman', 'Varietas', 'Tanggal Tanam', 'Status', 'Target PPM', 'Target pH'])

    # Tulis data
    tanaman_list = Tanaman.objects.all().values_list('jenis_tanaman', 'varietas', 'tanggal_tanam', 'status', 'target_ppm', 'target_ph')
    for tanaman in tanaman_list:
        writer.writerow(tanaman)

    return response

# View tambah_tanaman tetap sama fungsinya, hanya template yang akan kita ubah
def tambah_tanaman(request):
    if request.method == 'POST':
        form = TanamanForm(request.POST)
        if form.is_valid():
            tanaman_baru = form.save()
            # --- LOGIKA NOTIFIKASI 2a DIMULAI ---
            pesan = f"🌱 <b>TANAMAN BARU</b>\n\nTanaman <b>{tanaman_baru.get_jenis_tanaman_display()}</b> ({tanaman_baru.varietas}) berhasil ditambahkan ke sistem."
            kirim_pesan_telegram(pesan)
            # --- LOGIKA NOTIFIKASI 2a SELESAI ---
            return redirect('manajemen_tanaman')
    else:
        form = TanamanForm()
    return render(request, 'hidroponik/form_tanaman.html', {'form': form})

# View baru untuk menyediakan data ke grafik
def sensor_chart_data(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    data = tanaman.data_sensor.order_by('waktu_pencatatan')
    
    chart_data = {
        'labels': [d.waktu_pencatatan.strftime('%d %b %H:%M') for d in data],
        'ph_data': [d.ph for d in data],
        'suhu_data': [d.suhu for d in data],
        'nutrisi_data': [d.nutrisi_ppm for d in data],
        'ketinggian_air_data': [d.ketinggian_air if d.ketinggian_air is not None else 0 for d in data],
    }
    return JsonResponse(chart_data)

# View baru untuk update status
@require_POST
def update_status_tanaman(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    new_status = request.POST.get('status')
    
    valid_statuses = [s[0] for s in Tanaman.STATUS_CHOICES]
    if new_status in valid_statuses:
        tanaman.status = new_status
        if new_status == 'Panen':
            tanaman.tanggal_panen_estimasi = timezone.now().date()
        tanaman.save()
        # --- LOGIKA NOTIFIKASI 3 DIMULAI ---
        pesan = f"🔄 <b>UPDATE STATUS</b>\n\nStatus tanaman {tanaman} telah diubah menjadi <b>{new_status}</b>."
        kirim_pesan_telegram(pesan)
        # --- LOGIKA NOTIFIKASI 3 SELESAI ---
        
    return redirect('detail_tanaman', pk=tanaman.pk)
def riwayat_panen(request):
    # Ambil semua tanaman yang statusnya 'Panen'
    tanaman_panen = Tanaman.objects.filter(status='Panen').annotate(
        # Hitung durasi tanam dalam hari
        durasi_tanam=ExpressionWrapper(
            F('tanggal_panen_estimasi') - F('tanggal_tanam'),
            output_field=fields.DurationField()
        )
    ).order_by('-tanggal_panen_estimasi')

    context = {
        'semua_tanaman_panen': tanaman_panen
    }
    return render(request, 'hidroponik/riwayat_panen.html', context)

@require_POST # Memastikan view ini hanya bisa diakses via metode POST
def panen_tanaman(request, pk):
    tanaman = get_object_or_404(Tanaman, pk=pk)
    form = PanenForm(request.POST, instance=tanaman)
    
    if form.is_valid():
        panen_instance = form.save(commit=False)
        panen_instance.status = 'Panen'
        panen_instance.tanggal_panen_estimasi = timezone.now().date()
        panen_instance.save()
        # --- LOGIKA NOTIFIKASI 2b DIMULAI ---
        pesan = f"✅ <b>PANEN DICATAT</b>\n\nTanaman: {panen_instance}\nHasil: <b>{panen_instance.jumlah_hasil_angka} {panen_instance.get_satuan_hasil_display()}</b>\nCatatan: {panen_instance.catatan_panen}"
        kirim_pesan_telegram(pesan)
        # --- LOGIKA NOTIFIKASI 2b SELESAI ---
        return redirect('riwayat_panen')
        
    return redirect('detail_tanaman', pk=tanaman.pk)

def manajemen_pupuk(request):
    if request.method == 'POST':
        form = PupukNutrisiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manajemen_pupuk')

    form = PupukNutrisiForm()
    semua_pupuk = PupukNutrisi.objects.all().order_by('nama')
    context = {
        'form': form,
        'semua_pupuk': semua_pupuk
    }
    return render(request, 'hidroponik/manajemen_pupuk.html', context)

@require_POST
def hapus_pupuk(request, pk):
    pupuk = get_object_or_404(PupukNutrisi, pk=pk)
    pupuk.delete()
    return redirect('manajemen_pupuk')

def manajemen_inventaris(request):
    if request.method == 'POST':
        form = InventarisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manajemen_inventaris')

    form = InventarisForm()
    semua_item = InventarisItem.objects.all().order_by('nama_barang')
    context = {
        'form': form,
        'semua_item': semua_item
    }
    return render(request, 'hidroponik/manajemen_inventaris.html', context)

@require_POST
def hapus_inventaris_item(request, pk):
    item = get_object_or_404(InventarisItem, pk=pk)
    item.delete()
    return redirect('manajemen_inventaris')

def analisis_statistik(request):
    # Ambil semua tanaman yang sudah dipanen
    tanaman_panen = Tanaman.objects.filter(status='Panen')

    # 1. Rata-rata waktu tanam -> panen
    rata_rata_durasi = tanaman_panen.annotate(
        durasi=F('tanggal_panen_estimasi') - F('tanggal_tanam')
    ).aggregate(
        rata_rata=Avg('durasi')
    )['rata_rata'] or timedelta(days=0) # Beri nilai default jika belum ada panen

    # 2. Rekap hasil panen per bulan
    rekap_bulanan = tanaman_panen.annotate(
        bulan=TruncMonth('tanggal_panen_estimasi')
    ).values('bulan').annotate(
        jumlah_tanaman=Count('id'),
        # Konversi semua hasil ke gram untuk penjumlahan yang akurat
        total_gram=Sum(
            Case(
                When(satuan_hasil='kg', then=F('jumlah_hasil_angka') * 1000),
                default=F('jumlah_hasil_angka'),
                output_field=fields.FloatField()
            )
        )
    ).order_by('-bulan')

    # 3. Konsumsi pupuk (kita tampilkan sisa stok sebagai gambaran)
    stok_pupuk = PupukNutrisi.objects.all().order_by('nama')

    context = {
        'rata_rata_durasi_hari': rata_rata_durasi.days,
        'rekap_bulanan': rekap_bulanan,
        'stok_pupuk': stok_pupuk,
    }
    return render(request, 'hidroponik/analisis_statistik.html', context)


# View baru untuk data grafik
def produksi_chart_data(request):
    tanaman_panen = Tanaman.objects.filter(status='Panen')
    
    chart_data = tanaman_panen.annotate(
        bulan=TruncMonth('tanggal_panen_estimasi')
    ).values('bulan').annotate(
        total_gram=Sum(
            Case(
                When(satuan_hasil='kg', then=F('jumlah_hasil_angka') * 1000),
                default=F('jumlah_hasil_angka'),
                output_field=fields.FloatField()
            )
        )
    ).order_by('bulan')

    data = {
        'labels': [d['bulan'].strftime('%b %Y') for d in chart_data],
        'values': [d['total_gram'] for d in chart_data],
    }
    return JsonResponse(data)

def analisis_pertumbuhan(request):
    tanaman_aktif = Tanaman.objects.exclude(status='Panen')
    profil_tanaman = {p.nama: p for p in ProfilTanaman.objects.all()}

    hasil_analisis = []
    hari_ini = timezone.now().date()

    for tanaman in tanaman_aktif:
        profil = profil_tanaman.get(tanaman.get_jenis_tanaman_display())
        analisis = {'tanaman': tanaman}

        if not profil:
            analisis['status'] = 'Info Tidak Ditemukan'
            analisis['rekomendasi'] = 'Data referensi untuk jenis tanaman ini tidak ada.'
            analisis['estimasi_panen'] = '-'
        else:
            # 1. Estimasi Panen
            estimasi = tanaman.tanggal_tanam + timedelta(days=profil.estimasi_panen_hari)
            analisis['estimasi_panen'] = estimasi

            # 2. Status Pertumbuhan & Rekomendasi
            status = "Sehat"
            rekomendasi = "Semua parameter ideal."

            if hari_ini >= estimasi:
                status = "Siap Panen"
                rekomendasi = "Tanaman sudah melewati estimasi tanggal panen."
            else:
                sensor_terbaru = tanaman.data_sensor.first()
                if sensor_terbaru:
                    rekomendasi_list = []
                    # Cek pH
                    if not (profil.ph_ideal_min <= sensor_terbaru.ph <= profil.ph_ideal_max):
                        status = "Butuh Perhatian"
                        rekomendasi_list.append(f"pH air ({sensor_terbaru.ph}) di luar rentang ideal ({profil.ph_ideal_min}-{profil.ph_ideal_max}).")
                    # Cek PPM
                    if not (profil.ppm_ideal_min <= sensor_terbaru.nutrisi_ppm <= profil.ppm_ideal_max):
                        status = "Butuh Perhatian"
                        rekomendasi_list.append(f"PPM ({sensor_terbaru.nutrisi_ppm}) di luar rentang ideal ({profil.ppm_ideal_min}-{profil.ppm_ideal_max}).")

                    if rekomendasi_list:
                        rekomendasi = " ".join(rekomendasi_list)

            analisis['status'] = status
            analisis['rekomendasi'] = rekomendasi

        hasil_analisis.append(analisis)

    return render(request, 'hidroponik/analisis_pertumbuhan.html', {'hasil_analisis': hasil_analisis})

def kalkulator_nutrisi(request):
    return render(request, 'hidroponik/kalkulator_nutrisi.html')

def pengaturan_notifikasi(request):
    # Gunakan get_or_create untuk membuat object jika belum ada
    pengaturan, created = PengaturanTelegram.objects.get_or_create(pk=1)

    if request.method == 'POST':
        # Cek apakah ini form untuk kirim tes
        if 'kirim_tes' in request.POST:
            sukses = kirim_pesan_telegram("✅ Halo! Ini adalah notifikasi tes dari aplikasi HidroponikKu.")
            if sukses:
                messages.success(request, 'Notifikasi tes berhasil dikirim!')
            else:
                messages.error(request, 'Gagal mengirim notifikasi tes. Periksa kembali Token dan Chat ID Anda.')
            return redirect('pengaturan_notifikasi')

        # Jika bukan, ini adalah form untuk menyimpan pengaturan
        form = PengaturanTelegramForm(request.POST, instance=pengaturan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengaturan berhasil disimpan!')
            return redirect('pengaturan_notifikasi')

    form = PengaturanTelegramForm(instance=pengaturan)
    return render(request, 'hidroponik/pengaturan_notifikasi.html', {'form': form})

@require_POST # Pastikan hanya metode POST yang bisa mengakses view ini
def hapus_foto(request, pk):
    foto = get_object_or_404(FotoPerkembangan, pk=pk)
    # Simpan pk tanaman untuk redirect kembali ke halaman yang benar
    tanaman_pk = foto.tanaman.pk
    # Hapus file foto dari penyimpanan
    foto.foto.delete(save=True)
    # Hapus record foto dari database
    foto.delete()
    messages.success(request, 'Foto berhasil dihapus.')
    return redirect('detail_tanaman', pk=tanaman_pk)