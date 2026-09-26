# Naskah video Tugas 1 MMAI1001

**Judul:** Shortest Path Studio — Dijkstra dan Bellman–Ford

**Durasi sasaran:** sekitar 10 menit

**Status:** bahan rekaman. Ketiga anggota perlu merekam bagian masing-masing dan menunjukkan kontribusi nyata.
**Identitas:** Kelompok **X** sementara; ganti setelah nomor kelompok ditetapkan.

## Pembagian anggota dan alur layar

| Waktu | Anggota | Slide / layar | Bagian |
|---|---|---|---|
| 00:00–03:10 | Akhyar (260820701100010) | 1–2, lalu 3 | Tujuan tugas, data graf, format berkas, validasi masukan |
| 03:10–06:25 | Ahmad Faqih Al Ghifari (260820701100005) | 3–4, GUI | Dijkstra, visualisasi, langkah pencarian dan kontrol |
| 06:25–10:00 | Attar Rayyan Muhammad (260820701100011) | 5–8, GUI/terminal | Bellman–Ford, hasil, pengukuran, kasus khusus, simpulan |

Waktu di atas adalah panduan. Beri jeda alami saat berpindah layar dan menjalankan animasi. Sebelum merekam, setiap anggota meninjau bagian kodenya sendiri agar penjelasan kontribusi sesuai pekerjaan yang benar-benar dilakukan. Jika pembagian pekerjaan nyata berbeda, sesuaikan kalimat kontribusi dan tetap tampilkan ketiga anggota.

## Naskah bicara

### 00:00–01:05 — Akhyar, slide 1

“Assalamualaikum. Kami dari Kelompok X mempresentasikan Tugas 1 mata kuliah MMAI1001. Anggota kelompok kami adalah saya, Akhyar, Ahmad Faqih Al Ghifari, dan Attar Rayyan Muhammad. Aplikasi yang kami kerjakan bernama Shortest Path Studio. Tugasnya adalah mencari rute dengan bobot total paling kecil pada graf berbobot, lalu memperlihatkan proses pencariannya melalui antarmuka grafis. Kami menggunakan Dijkstra dan Bellman–Ford supaya dua pendekatan yang berbeda bisa dibandingkan pada data yang sama.”

### 01:05–02:20 — Akhyar, slide 2

“Data dibaca dari `graf.txt`. Berkas ini berisi kamus ketetanggaan, kemudian pasangan simpul awal dan tujuan. Setiap pasangan tetangga menyimpan bobot sisi. Arah sisi mengikuti data yang tertulis. Jadi, apabila hanya ada V1 menuju V2, kami tidak otomatis menambahkan sisi balik dari V2 ke V1. Pada contoh utama dari soal terdapat 15 simpul dan 36 sisi. Kita akan melihat dua pertanyaan pada graf itu: V1 ke V15 dan V1 ke V10. Contoh lain memakai simpul B ke H. Hasil yang dicari mencakup urutan simpul pada jalur, total bobot, dan waktu algoritma.”

### 02:20–03:10 — Akhyar, tunjukkan `graf.txt` dan kembali ke slide 3

“Pembacaan file memakai parser literal, bukan menjalankan file sebagai kode Python. Parser menerima nama variabel `graph` ataupun `graf`, lalu memeriksa semua simpul, tujuan, dan bobot. Bobot harus berupa angka yang terbatas; tujuan sisi harus terdaftar sebagai simpul. Masukan yang rusak menghasilkan pesan kesalahan yang bisa dibaca. Pemisahan ini membantu kami memakai graf yang sama di GUI maupun di mode terminal. Sekarang Faqih menjelaskan algoritma pertama dan tampilan prosesnya.”

### 03:10–04:20 — Faqih, slide 3

“Dijkstra menyimpan perkiraan jarak terpendek dari titik awal. Algoritma mengambil simpul dengan jarak terkecil dari heap, kemudian mencoba memperbaiki jarak tetangganya. Bila ada rute yang lebih ringan, jarak dan pendahulu simpul itu diperbarui. Setelah tujuan diproses, pendahulu ditelusuri balik untuk membentuk jalur. Syarat pentingnya adalah semua bobot sisi tidak negatif. Bila terdapat bobot negatif, pilihan simpul yang sudah dianggap final dapat salah. Implementasi ini menghentikan Dijkstra secara jelas pada kondisi tersebut. Dengan daftar ketetanggaan dan heap, kompleksitas terburuknya O((V + E) log V).”

### 04:20–05:30 — Faqih, slide 4 lalu buka GUI

“Ini tampilan aplikasi yang dijalankan di Windows. Lingkaran mewakili simpul, panah menunjukkan arah sisi, dan angka di dekat panah adalah bobot. Di bagian atas kita memilih simpul awal dan akhir serta memuat file graf. Panel hasil memperlihatkan kedua algoritma. Waktu yang tertera diukur khusus untuk komputasi algoritma; waktu menggambar dan menunggu animasi tidak dihitung. Saat proses berjalan, warna simpul dan sisi berubah sehingga urutan eksplorasi dapat diamati.”

### 05:30–06:25 — Faqih, demo GUI

“Saya pilih V1 sebagai awal dan V15 sebagai tujuan. Setelah menekan putar, perhatikan pembaruan simpul yang sedang diperiksa. Saya jeda dan maju satu langkah untuk melihat keadaan berikutnya. Kecepatan dapat diubah tanpa mengubah hasil pencarian. Tombol ulang mengembalikan animasi ke awal. Jika ingin melihat algoritma lain, saya pilih Bellman–Ford pada kontrol metode. Keduanya akan memberi jalur yang sama untuk contoh ini. Selanjutnya Attar menjelaskan mengapa hasilnya sama dan kapan Bellman–Ford diperlukan.”

### 06:25–07:10 — Attar, slide 3 atau layar hasil

“Bellman–Ford memperbaiki estimasi jarak dengan mengendurkan seluruh sisi berulang sampai jumlah iterasi yang diperlukan atau sampai tidak ada perubahan. Karena tidak menetapkan simpul secara permanen seperti Dijkstra, metode ini mendukung sisi berbobot negatif. Setelah iterasi utama, masih adanya perbaikan menandakan kemungkinan siklus negatif. Aplikasi memeriksa apakah pengaruh siklus itu dapat mencapai tujuan; jika iya, tidak ada bobot minimum yang terdefinisi. Batas waktu terburuk Bellman–Ford adalah O(VE).”

### 07:10–08:00 — Attar, slide 5

“Kami memeriksa ketiga contoh resmi dari PDF soal. Untuk V1 ke V15, jalurnya V1, V2, V5, V9, V12, V15 dengan bobot 505. Untuk V1 ke V10, jalurnya V1, V4, V6, V10 dengan bobot 400. Pada contoh B ke H, jalurnya B, C, F, E, H dengan bobot 9. Kedua algoritma memberikan bobot yang sama pada ketiga kasus tersebut. Kami juga menjumlahkan bobot sisi di setiap jalur untuk memastikan hasilnya sesuai dengan jalur yang ditampilkan.”

### 08:00–08:55 — Attar, slide 6

“Untuk membandingkan waktu, tiap kasus dijalankan 100 kali sebagai pemanasan dan diukur 1.000 kali pada mesin yang sama. Angka pada slide adalah median dalam mikrodetik. Pada V1 ke V15, Dijkstra 18,1 mikrodetik dan Bellman–Ford 43,1 mikrodetik. Dua contoh lain menunjukkan arah yang sama: Dijkstra lebih cepat. Ini sesuai dengan perbedaan kompleksitasnya, tetapi grafnya kecil dan angka waktu bisa berubah pada mesin atau beban sistem yang berbeda. Karena itu kami menyebut metode ukur dan satuannya, serta tidak memasukkan animasi GUI.”

### 08:55–09:35 — Attar, slide 7

“Selain contoh utama, kami menguji tujuan yang tidak terjangkau, awal yang sama dengan tujuan, jalur dengan bobot seri, masukan yang rusak, bobot negatif, dan siklus negatif. Jika tujuan tidak terjangkau, aplikasi menampilkan bahwa jalur tidak ada. Jika awal sama dengan tujuan, hasilnya satu simpul berbobot nol. Dijkstra menjelaskan bahwa ia tidak berlaku untuk graf berbobot negatif; Bellman–Ford tetap menghitung kecuali ada siklus negatif yang memengaruhi tujuan.”

### 09:35–10:00 — Attar, slide 8 dan tutup

“Kesimpulannya, untuk tiga contoh tugas yang berbobot tidak negatif, kedua algoritma menghasilkan bobot optimal yang sama, sedangkan Dijkstra lebih cepat pada pengukuran kami. Bellman–Ford memberi dukungan tambahan untuk bobot negatif dan deteksi siklus negatif. Aplikasi dapat dijalankan lewat GUI, dan tersedia opsi `--cli` untuk komputer tanpa layar. Terima kasih. Wassalamualaikum.”

## Urutan demo dan pemeriksaan rekaman

1. Buka `graf.txt` sebentar agar format masukan terlihat, lalu jalankan `python MMAIKelompokX.py` dari folder tugas.
2. Atur V1 → V15. Tampilkan kedua hasil; bobot masing-masing harus **505**.
3. Jalankan animasi Dijkstra; tunjukkan **putar**, **jeda**, **langkah**, **ulang**, dan pengaturan kecepatan.
4. Beralih ke Bellman–Ford. Tunjukkan jalur yang sama dan waktu algoritma yang ditampilkan terpisah.
5. Jika layar GUI sulit direkam, tunjukkan hasil terminal dengan `python MMAIKelompokX.py --cli` sebagai cadangan, tetapi tetap perlihatkan GUI pada rekaman utama.
6. Pastikan identitas ketiga anggota tampak/terdengar sesuai aturan dosen. Jangan mencantumkan klaim kontribusi yang tidak sesuai kegiatan nyata.
7. Ganti **X** pada nama file Python dan sampul laporan/presentasi setelah nomor kelompok resmi diketahui. Rekam dan gabungkan video final setelah ketiga rekaman anggota tersedia.
