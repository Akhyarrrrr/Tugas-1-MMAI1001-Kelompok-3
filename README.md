# Tugas 1 MMAI1001 — Kelompok 3

Program ini mencari jalur terpendek pada graf berbobot menggunakan Dijkstra dan Bellman–Ford. Antarmuka Tkinter menampilkan graf, jalur hasil, bobot minimum, waktu hitung, dan langkah pencarian. Kode aplikasi hanya menggunakan pustaka standar Python.

**Anggota:** Akhyar (260820701100010), Ahmad Faqih Al Ghifari (260820701100005), dan Attar Rayyan Muhammad (260820701100011).

## Menjalankan

Gunakan Python 3.10 atau lebih baru dengan Tkinter. Di Windows, klik `Jalankan Aplikasi.bat`, atau jalankan:

```powershell
python MMAIKelompok3.py
```

Tanpa jendela grafis, gunakan mode teks. Pilihan `--start` dan `--goal` mengganti simpul dari baris terakhir file tanpa mengubah berkasnya:

```powershell
python MMAIKelompok3.py --cli
python MMAIKelompok3.py --cli --start V1 --goal V10
python MMAIKelompok3.py --cli contoh/graf_BH.txt
```

Untuk mengulangi pengukuran pada laporan, setiap algoritma dijalankan 100 kali sebagai pemanasan, lalu 1.000 kali untuk menghitung median waktu fungsi pencarian:

```powershell
python MMAIKelompok3.py --benchmark --repetitions 1000 --start V1 --goal V15
python MMAIKelompok3.py --benchmark --repetitions 1000 --start V1 --goal V10
python MMAIKelompok3.py --benchmark --repetitions 1000 contoh/graf_BH.txt
```

Waktu tidak mencakup pembacaan file, tampilan GUI, atau jeda animasi. Nilai mikrodetik bisa berbeda menurut mesin dan beban sistem.

## Format graf

File memuat satu dictionary literal Python bernama `graph` atau `graf`, lalu pasangan simpul awal dan tujuan pada baris terakhir:

```text
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4},
    'C': {},
}
A C
```

Sisi mengikuti arah yang tertulis. Jika diperlukan arah balik, tulis sisi balik secara terpisah. Setiap simpul tujuan harus memiliki entri dictionary, dan bobot harus berupa angka terhingga. Parser membaca literal sebagai data, bukan menjalankan kode di dalam file. Bentuk `BH` tanpa spasi pada contoh soal diterima hanya jika `B` dan `H` adalah dua simpul satu huruf yang tidak ambigu.

Dijkstra berlaku untuk graf dengan bobot nonnegatif. Bila ada sisi negatif, aplikasi menampilkan alasan Dijkstra tidak dijalankan dan tetap mencoba Bellman–Ford. Siklus negatif yang dapat memengaruhi tujuan dilaporkan sebagai jalur minimum yang tidak terdefinisi.

## Menggunakan GUI

1. Buka aplikasi; `graf.txt` contoh dosen langsung dimuat. Gunakan **Buka file graf** untuk data lain.
2. Pilih **Awal** dan **Tujuan**, lalu tekan **Hitung jalur**. Kartu di kanan menampilkan hasil masing-masing algoritma.
3. Pilih algoritma pada **Langkah pencarian**. Gunakan **Putar/Jeda**, **Mundur**, **Maju**, bilah kemajuan, atau **Ke awal**. Simpul pada graf dapat diseret.
4. Garis biru kehijauan menunjukkan jalur terbaik; hijau menandai awal, merah kecokelatan menandai tujuan, dan jingga menandai sisi yang sedang diperiksa. Panel hasil dapat digulir pada jendela kecil.

Hasil contoh resmi: V1–V15 berbobot **505**, V1–V10 berbobot **400**, dan B–H berbobot **9**. Jalankan pengujian dengan `python -m unittest -v`; sepuluh uji tersedia.

## Berkas yang digunakan

- `MMAIKelompok3.py`: pintu masuk GUI, mode teks, dan benchmark.
- `shortest_path.py`: parser dan kedua algoritma.
- `graph_gui.py`: gambar graf dan animasi Tkinter.
- `graf.txt` dan `contoh/graf_BH.txt`: data contoh dari soal.
- `test_shortest_path.py`: uji hasil resmi dan kasus batas.
- `Laporan_Tugas_1_MMAI1001_Kelompok_3.docx` dan `.pdf`: laporan yang dapat diedit dan versi siap baca.
- `Tugas 1 MMAI1001 2026.pdf`: soal asli.

Video presentasi sekitar sepuluh menit tetap perlu direkam sebagai berkas pengumpulan terpisah dengan kontribusi ketiga anggota.
