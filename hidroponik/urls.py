# hidroponik/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Pastikan tidak ada tanda kurung () setelah nama view
    path('', views.dashboard, name='dashboard'),
    
    # URL Manajemen Tanaman
    path('tanaman/', views.manajemen_tanaman, name='manajemen_tanaman'),
    path('tanaman/tambah/', views.tambah_tanaman, name='tambah_tanaman'),
    path('tanaman/<int:pk>/', views.detail_tanaman, name='detail_tanaman'),
    path('tanaman/<int:pk>/hapus/', views.hapus_tanaman, name='hapus_tanaman'),
    path('tanaman/<int:pk>/data/tambah/', views.tambah_data_sensor, name='tambah_data_sensor'),

    # URL Panen
    path('tanaman/<int:pk>/update_status/', views.update_status_tanaman, name='update_status_tanaman'),
    path('tanaman/<int:pk>/panen/', views.panen_tanaman, name='panen_tanaman'),
    path('riwayat-panen/', views.riwayat_panen, name='riwayat_panen'),

    # URL Inventaris & Pupuk
    path('pupuk-nutrisi/', views.manajemen_pupuk, name='manajemen_pupuk'),
    path('pupuk-nutrisi/<int:pk>/hapus/', views.hapus_pupuk, name='hapus_pupuk'),
    path('inventaris/', views.manajemen_inventaris, name='manajemen_inventaris'),
    path('inventaris/<int:pk>/hapus/', views.hapus_inventaris_item, name='hapus_inventaris_item'),

    # URL Analisis & Fitur Lain
    path('analisis/', views.analisis_statistik, name='analisis_statistik'),
    path('analisis/chart-data/', views.produksi_chart_data, name='produksi_chart_data'),
    path('analisis-pertumbuhan/', views.analisis_pertumbuhan, name='analisis_pertumbuhan'),
    path('kalkulator-nutrisi/', views.kalkulator_nutrisi, name='kalkulator_nutrisi'),
    path('pengaturan-notifikasi/', views.pengaturan_notifikasi, name='pengaturan_notifikasi'),
    path('tanaman/<int:pk>/chart_data/', views.sensor_chart_data, name='sensor_chart_data'),
    
    # URL Export
    path('export/csv/', views.export_csv, name='export_csv'),
    
]