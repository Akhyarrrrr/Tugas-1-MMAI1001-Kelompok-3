# Maze BFS Studio

Maze BFS Studio adalah aplikasi interaktif untuk memvisualisasikan **Breadth First Search (BFS)** pada maze. Aplikasi membaca format tugas resmi, memperlihatkan antrean FIFO dan urutan kunjungan, lalu menampilkan lintasan keluar terpendek.

**Dibuat oleh:** Akhyar — 260820701100010  
**Mata kuliah:** Kecerdasan Artifisial (MMAI1001)

## Fitur

- Editor maze dengan mode dinding, jalan, dan titik mulai.
- Animasi BFS dengan play, pause, langkah maju/mundur, timeline, dan pengaturan kecepatan.
- Inspector untuk petak aktif, jarak, jumlah petak ditemukan, dan isi frontier queue.
- Generator maze acak yang selalu memiliki sedikitnya satu jalan keluar.
- Impor dan ekspor `maze.txt` sesuai format tugas.
- Validasi input serta tampilan responsif dan aksesibel.
- CLI resmi yang tetap mencetak satu bilangan hasil.

## Menjalankan aplikasi

### Cara termudah di Windows

Klik dua kali **`Jalankan Aplikasi.bat`**. Terminal akan menampilkan alamat lokal dan browser terbuka otomatis. Tutup terminal atau tekan `Ctrl+C` untuk menghentikan server.

### Melalui terminal

Syarat: Python 3.10 atau lebih baru.

```powershell
python app.py
```

Browser akan membuka aplikasi pada alamat `http://127.0.0.1:<port>`. Port dipilih otomatis agar tidak bentrok dengan aplikasi lain.

Untuk menjalankan solusi tugas versi CLI:

```powershell
python maze.py
```

Dengan `maze.txt` bawaan, keluarannya tepat:

```text
17
```

> Jangan membuka `web/index.html` langsung. Frontend memerlukan API Python dari `app.py`.

## Format `maze.txt`

```text
N M
baris maze ke-1
...
baris maze ke-N
A B
```

- `N M`: jumlah baris dan kolom.
- Setiap sel hanya boleh bernilai `-1` (dinding) atau `0` (jalan).
- `A B`: koordinat awal berbasis 1, sesuai format soal.
- Gerakan hanya atas, bawah, kiri, dan kanan.
- Jumlah langkah mencakup petak awal dan petak keluar.
- Program menghasilkan `-1` bila tidak ada exit batas yang dapat dicapai.

## Pengujian

Adapter Vercel memakai Flask. Instal dependensi hanya jika ingin menjalankan seluruh test atau build Vercel; aplikasi lokal dan CLI tetap menggunakan pustaka standar Python.

```powershell
python -m pip install -r requirements.txt
python -m py_compile maze.py app.py api/index.py test_maze.py
node --check web/app.js
python -m unittest -v
```

## Arsitektur

```text
maze.py              Algoritma BFS, parsing, dan validasi utama
app.py               Server lokal berbasis standard library
api/index.py         Adapter Flask untuk Python Functions Vercel
maze.txt             Contoh resmi dengan hasil 17
web/                  HTML, CSS, JavaScript, dan favicon
test_maze.py          Pengujian algoritma, server lokal, dan Vercel
vercel.json           Konfigurasi hosting frontend dan Python Function
```

`maze.py` adalah satu-satunya sumber kebenaran algoritma. Server lokal dan Vercel hanya menerjemahkan request HTTP ke fungsi yang sama, sehingga hasil web dan CLI tetap konsisten.

## Menyiapkan GitHub

Repository lokal sudah diinisialisasi pada branch `main`, tetapi belum di-stage, commit, atau push. Setelah membuat repository kosong di GitHub, jalankan:

```powershell
git add .
git commit -m "feat: build interactive BFS maze studio"
git remote add origin https://github.com/USERNAME/maze-bfs-studio.git
git push -u origin main
```

Ganti `USERNAME` dan nama repository sesuai akun GitHub. Jangan centang pembuatan README atau `.gitignore` baru di GitHub karena keduanya sudah tersedia di proyek ini.

## Menayangkan di Vercel

GitHub menyimpan kode, sedangkan Vercel menjalankan frontend dan API Python. GitHub Pages tidak cocok untuk versi ini karena hanya menyediakan hosting statis dan tidak menjalankan Python server-side.

### Melalui dashboard

1. Push proyek ke GitHub.
2. Buka Vercel dan pilih **Add New → Project**.
3. Impor repository `maze-bfs-studio`.
4. Biarkan root directory pada folder utama repository.
5. Vercel membaca `vercel.json` dan `requirements.txt`; pilih **Deploy**.

### Melalui CLI

```powershell
npx vercel
npx vercel --prod
```

Perintah pertama menghubungkan proyek dan membuat preview deployment. Perintah kedua membuat production deployment. Folder `.vercel` bersifat lokal dan sudah diabaikan Git.

## Troubleshooting

- **`python` tidak dikenali:** instal Python dan aktifkan opsi *Add Python to PATH*.
- **Browser tidak terbuka:** salin alamat yang dicetak terminal ke browser.
- **Port berubah:** normal; server memilih port kosong setiap dijalankan.
- **Impor ditolak:** periksa dimensi, nilai sel, koordinat, dan pastikan titik awal bukan dinding.
- **Test gagal karena Flask:** jalankan `python -m pip install -r requirements.txt`.
- **Vercel menampilkan 404 API:** pastikan `api/index.py`, `maze.py`, `maze.txt`, dan `vercel.json` ikut ter-push.

## Batas proyek

File `Maze 24.pdf` adalah dokumen soal asli dan dipertahankan tanpa perubahan. Proyek ini belum mencakup laporan, arsip kelompok, maupun pengunggahan ke LMS.
