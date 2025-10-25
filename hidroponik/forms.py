# hidroponik/forms.py
from django import forms
from .models import Tanaman, DataSensor
from .models import LogAktivitas
from .models import PupukNutrisi
from .models import InventarisItem
from .models import PengaturanTelegram
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


class TanamanForm(forms.ModelForm):
    class Meta:
        model = Tanaman
        fields = [
            'jenis_tanaman', 'varietas', 'tanggal_tanam', 'media_tanam', 
            'posisi', 'target_ppm', 'target_ph', 'target_suhu',
            'tanggal_panen_estimasi', 'deskripsi'
        ]
        widgets = {
            'tanggal_tanam': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_panen_estimasi': forms.DateInput(attrs={'type': 'date'}),
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
        }


class DataSensorForm(forms.ModelForm):
    class Meta:
        model = DataSensor
        # Sesuaikan dengan nama field baru di model
        fields = ['ph', 'suhu', 'nutrisi_ppm', 'ketinggian_air']
        
# Form Baru
class LogAktivitasForm(forms.ModelForm):
    class Meta:
        model = LogAktivitas
        # Tambahkan field baru di sini
        fields = ['jenis_aktivitas', 'pupuk_yang_digunakan', 'jumlah_yang_digunakan', 'catatan']
        widgets = {
            'catatan': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Membuat label lebih ramah
        self.fields['pupuk_yang_digunakan'].label = "Pilih Pupuk/Nutrisi"
        self.fields['jumlah_yang_digunakan'].label = "Jumlah Digunakan"

        
# FORM BARU UNTUK MODAL PANEN
class PanenForm(forms.ModelForm):
    class Meta:
        model = Tanaman
        fields = ['jumlah_hasil_angka', 'satuan_hasil', 'catatan_panen']
        widgets = {
            'catatan_panen': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('jumlah_hasil_angka', css_class='form-group col-md-7 mb-0'),
                Column('satuan_hasil', css_class='form-group col-md-5 mb-0'),
                css_class='form-row'
            ),
            'catatan_panen'
        )

# FORM BARU
class PupukNutrisiForm(forms.ModelForm):
    class Meta:
        model = PupukNutrisi
        fields = ['nama', 'pabrikan', 'jumlah', 'satuan', 'deskripsi']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nama'].widget.attrs['placeholder'] = 'Nama Pupuk/Nutrisi *'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nama',
            'pabrikan',
            Row(
                Column('jumlah', css_class='form-group col-md-8 mb-0'),
                Column('satuan', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'deskripsi'
        )
        self.helper.form_show_labels = False # Sembunyikan label bawaan
        
class InventarisForm(forms.ModelForm):
    class Meta:
        model = InventarisItem
        fields = ['nama_barang', 'jumlah', 'kategori', 'catatan']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menggunakan crispy forms akan otomatis memakai label dari model
        # jadi kita tidak perlu placeholder manual
        self.helper = FormHelper()
        self.helper.form_tag = False 
        
class PengaturanTelegramForm(forms.ModelForm):
    class Meta:
        model = PengaturanTelegram
        fields = ['bot_token', 'chat_id']