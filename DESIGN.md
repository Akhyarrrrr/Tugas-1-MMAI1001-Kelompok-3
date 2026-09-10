---
name: Maze BFS Studio
description: A precise interactive light table for understanding breadth first search
colors:
  canvas: "oklch(96.8% 0.008 165)"
  surface: "oklch(99.2% 0.004 165)"
  surface-strong: "oklch(93.6% 0.012 165)"
  ink: "oklch(22% 0.027 170)"
  ink-soft: "oklch(43% 0.026 170)"
  line: "oklch(85% 0.018 165)"
  wall: "oklch(29% 0.027 170)"
  active-vermilion: "oklch(57% 0.19 33)"
  frontier-cyan: "oklch(68% 0.11 207)"
  frontier-soft: "oklch(91% 0.035 207)"
  path-amber: "oklch(79% 0.15 84)"
  exit-green: "oklch(57% 0.13 151)"
  focus-blue: "oklch(52% 0.16 252)"
typography:
  title:
    fontFamily: "Bahnschrift, Segoe UI Variable Text, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Bahnschrift, Segoe UI Variable Text, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  data:
    fontFamily: "Cascadia Mono, monospace"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "14px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "24px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.active-vermilion}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    height: "42px"
  button-quiet:
    backgroundColor: "{colors.surface-strong}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    height: "40px"
  maze-cell:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
---

# Design System Maze BFS Studio

## Overview

**Creative North Star: "The Architect's Light Table"**

Maze BFS Studio terasa seperti instrumen pemetaan yang digunakan untuk menelaah sebuah sistem dengan tenang. Permukaannya terang dan dingin, komponen tidak berlomba menarik perhatian, dan maze menjadi artefak utama. Presisi datang dari ritme, tipografi, serta keadaan yang konsisten, bukan dari dekorasi teknologi.

Gerakan hanya muncul ketika algoritma berubah keadaan: frontier bertambah, petak aktif berpindah, atau lintasan akhir dibentuk. Tampilan menghindari neon, kaca dekoratif, gradient text, dan tumpukan kartu identik.

**Key Characteristics:**

- Cool light-table surfaces with graphite structure
- Vermilion current state, cyan search state, amber solution path
- Compact technical typography and clear spatial hierarchy
- State-driven motion with a complete reduced-motion alternative

## Colors

Palet memisahkan struktur, proses, dan hasil dengan peran warna yang tetap.

### Primary

- **Active Vermilion:** hanya untuk petak aktif dan tindakan utama.

### Secondary

- **Frontier Cyan:** menandai ruang yang ditemukan dan antrean pencarian.
- **Path Amber:** hanya muncul setelah solusi selesai direkonstruksi.
- **Exit Green:** mengidentifikasi exit akhir dan status berhasil.

### Neutral

- **Cool Canvas:** latar kerja utama tanpa tint krem.
- **Graphite Ink:** teks, transport bar, dan dinding maze.
- **Soft Ink:** teks penjelas yang tetap melampaui kontras AA.

**The Earned Color Rule.** Warna jenuh hanya muncul ketika state algoritma memberinya makna.

## Typography

**Display Font:** Bahnschrift
**Body Font:** Bahnschrift dengan Segoe UI Variable Text sebagai fallback
**Label/Mono Font:** Cascadia Mono

**Character:** Tipografi terasa seperti alat ukur modern: ringkas, tajam, dan mudah dipindai. Mono digunakan hanya untuk koordinat, angka, antrean, dan shortcut.

### Hierarchy

- **Title** (700, 23px, 1.15): judul area kerja utama.
- **Headline** (700, 17px, 1.2): judul inspector.
- **Body** (400, 15px, 1.5): teks antarmuka umum.
- **Label** (600, 11–12px): kontrol dan metadata.
- **Data** (600, 11–15px): koordinat, metrik, dan queue.

**The Data Voice Rule.** Mono tidak digunakan sebagai gaya; ia hanya menandai data yang dapat dihitung.

## Layout

Desktop menggunakan kanvas fleksibel dan inspector tetap 330px. Semua transport kontrol harus terlihat dalam satu viewport laptop. Di bawah 980px inspector berpindah ke bawah; di bawah 680px toolbar dan transport membentuk susunan vertikal yang tetap mempertahankan target sentuh.

Spacing memakai langkah 6, 10, 14, 24, dan 28px. Maze selalu mempertahankan rasio dimensinya serta memiliki ruang kosong yang cukup untuk dibaca sebagai satu objek.

## Elevation & Depth

Sistem flat secara default. Kedalaman dibentuk oleh perbedaan tonal; bayangan hanya berupa inset tipis pada frame maze atau feedback state. Tidak ada kartu ghost dengan border sekaligus shadow lebar.

**The Flat Instrument Rule.** Struktur tetap tenang; state aktif yang bergerak, bukan permukaan dekoratif.

## Shapes

Kontrol memakai sudut 6–10px, frame utama 14px, dan tombol play berbentuk lingkaran karena fungsinya sebagai transport utama. Sel maze memakai sudut kecil agar grid terasa presisi tanpa menjadi spreadsheet kaku.

## Components

### Buttons

- **Shape:** persegi lunak 6px; play menjadi lingkaran 42px.
- **Primary:** vermilion dengan ikon putih dan active scale 0.97.
- **Hover / Focus:** perubahan tonal 180ms dan focus ring biru 3px.
- **Quiet:** tonal surface tanpa shadow dekoratif.

### Cards / Containers

- **Corner Style:** 10–14px.
- **Background:** surface atau canvas sesuai hierarki.
- **Shadow Strategy:** tonal layering dan inset line.
- **Internal Padding:** 14–28px sesuai tingkat hierarki.

### Inputs / Fields

- **Style:** field kompak, permukaan canvas, garis tonal, radius 6px.
- **Focus:** focus ring biru yang tidak bergantung pada perubahan warna isi.
- **Error / Disabled:** pesan eksplisit dan opacity yang tetap terbaca.

### Maze Cell

Setiap sel adalah tombol grid semantik. Class state menentukan dinding, visited, frontier, current, path, start, dan exit; marker serta label selalu mendampingi warna.
Titik awal memakai ikon navigation/origin berwarna vermilion, bukan huruf, dengan nama aksesibel tetap “titik mulai”. Kredit pembuat tampil tenang pada status bar dan tidak boleh mengurangi area maze.

## Do's and Don'ts

### Do:

- **Do** pertahankan maze sebagai elemen terbesar pada layar.
- **Do** gunakan motion 150–250ms untuk feedback state dan delay terpisah untuk playback BFS.
- **Do** uji seluruh state pada keyboard dan reduced motion.

### Don't:

- **Don't** memakai warna jenuh pada state pasif.
- **Don't** menambahkan gradient text, glassmorphism, particle, atau ilustrasi generatif.
- **Don't** menyembunyikan arti state di balik warna saja.
