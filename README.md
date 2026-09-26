# Shortest Path Studio

Program Tugas 1 MMAI1001 ini membaca graf berbobot dari `graf.txt`, mencari jalur terpendek dengan **Dijkstra** dan **Bellman–Ford**, lalu membandingkan jalur, bobot minimum, dan waktu running. GUI Tkinter menampilkan graf dan perkembangan pencarian secara bertahap.

**Anggota kelompok:** Akhyar (260820701100010), Ahmad Faqih Al Ghifari (260820701100005), dan Attar Rayyan Muhammad (260820701100011).

> **Sebelum dikumpulkan:** nomor kelompok belum ditetapkan. Ganti huruf `X` pada `MMAIKelompokX.py` serta sampul laporan dan slide dengan nomor resmi. Nama anggota di atas adalah identitas yang diberikan kelompok.

## Menjalankan

Gunakan Python 3.10 atau lebih baru dengan Tkinter. Pada Windows, klik dua kali `Jalankan Aplikasi.bat`, atau jalankan dari terminal:

```powershell
python MMAIKelompokX.py
```

Tidak ada paket Python tambahan untuk menjalankan program. Jika Tkinter tidak tersedia pada instalasi Linux, pasang paket Tkinter yang sesuai distribusi Python Anda. Mode teks tetap dapat berjalan tanpa layar atau Tkinter:

```powershell
python MMAIKelompokX.py --cli
python MMAIKelompokX.py --cli contoh/graf_BH.txt
python MMAIKelompokX.py --benchmark --repetitions 1000
python -m unittest -v
```

File argumen opsional dapat memakai path absolut atau relatif terhadap terminal. Tanpa argumen, program membaca `graf.txt` di folder yang sama dengan berkas utama, sehingga dapat dibuka dari direktori lain.

## Format file graf

Isi file berupa satu dictionary literal Python bernama `graph` atau `graf`, diikuti baris terakhir berisi simpul awal dan akhir yang dipisahkan spasi:

```text
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4},
    'C': {},
}
A C
```

Setiap sisi mengikuti arah yang tertulis. Jika arah balik diperlukan, tuliskan secara eksplisit pada daftar tetangga simpul balik. Semua simpul tujuan harus punya entri dictionary sendiri. Bobot boleh berupa bilangan bulat atau desimal terhingga. Program membaca file sebagai data literal dan tidak mengeksekusi kode di dalamnya.

Untuk graf berbobot nonnegatif, kedua algoritma dijalankan. Jika ada bobot negatif, hanya Bellman–Ford yang berlaku. Program melaporkan kesalahan bila siklus negatif yang dapat dicapai dari awal juga dapat menuju tujuan. Jika tujuan tak terjangkau, jalur dan bobot ditampilkan sebagai tidak ada.

## Menggunakan GUI

1. Buka aplikasi. Contoh resmi `graf.txt` langsung dimuat.
2. Pilih simpul **Awal** dan **Akhir**, kemudian tekan **Jalankan kedua algoritma**. File yang berbeda dapat dibuka dengan **Buka graf.txt**.
3. Bandingkan hasil pada panel kanan. Pilih algoritma pada **Proses yang ditampilkan**.
4. Gunakan **Putar/Jeda**, tombol langkah, bilah kemajuan, dan pilihan kecepatan. Jalur akhir berwarna kuning. Simpul dapat diseret agar gambar lebih mudah dibaca.

Waktu yang ditampilkan adalah durasi fungsi pencarian menggunakan `perf_counter_ns()`, dinyatakan dalam mikrodetik. Pembuatan animasi dan penggambaran GUI tidak termasuk. Angka waktu dapat berubah antar mesin dan antar percobaan; `--benchmark` menampilkan median dari jumlah percobaan yang dipilih.

## Hasil contoh dosen

| Awal–akhir | Jalur minimum | Bobot |
|---|---|---:|
| V1–V15 | V1 → V2 → V5 → V9 → V12 → V15 | 505 |
| V1–V10 | V1 → V4 → V6 → V10 | 400 |
| B–H | B → C → F → E → H | 9 |

Contoh B–H tersedia dalam `contoh/graf_BH.txt`. Untuk V1–V10, ganti simpul akhir di GUI menjadi `V10` atau ubah baris terakhir salinan `graf.txt`.

## Isi paket

- `MMAIKelompokX.py`: pintu masuk GUI, mode teks, dan benchmark.
- `shortest_path.py`: parser aman dan implementasi kedua algoritma.
- `graph_gui.py`: tampilan dan animasi Tkinter.
- `graf.txt` dan `contoh/graf_BH.txt`: data contoh dosen.
- `test_shortest_path.py`: uji hasil resmi dan kasus batas.
- `Laporan_Tugas_1_Shortest_Path.docx` serta `.pdf`: laporan proyek.
- `presentasi/Presentasi_Tugas_1_Shortest_Path.pptx` dan `presentasi/Naskah_Video_Presentasi.md`: bahan rekaman kelompok.

Video akhir ±10 menit harus memakai kontribusi nyata ketiga anggota. Naskah dan slide disiapkan untuk direkam; berkas video akhir belum ada sampai rekaman anggota tersedia. Tidak ada pengunggahan otomatis ke e-learning USK.
