# Cara Penggunaan HTTP Chat Room dengan Enkripsi DES

## Tim Pengembang

| Nama | NRP |
|------|-----|
| Muhammad Danis Hadriansyah | 5025221239 |
| Fathurazka Gamma Syuhada | 5025231246 |

Program ini terdiri dari dua komponen utama:
1. **HTTP Server** (`http_server.py`) - Server chat room yang mengelola komunikasi
2. **HTTP Client** (`http_client.py`) - Client untuk bergabung dan berkirim pesan

## Fitur Utama

- **Enkripsi DES**: Semua pesan dienkripsi menggunakan algoritma DES dengan kunci 8-byte
- **Chat Room**: Mendukung komunikasi multi-client dalam satu ruang chat
- **HTTP Protocol**: Menggunakan protokol HTTP untuk komunikasi client-server
- **Real-time Messaging**: Pesan ditampilkan secara real-time antar client

## Prerequisites

Pastikan Anda memiliki:
- Python 3.10.x terinstall
- Library `requests` untuk client (`pip install requests`)
- Koneksi internet (jika LocalTunnel diperlukan)

## Langkah-langkah Penggunaan

### 1. Menjalankan HTTP Server

Buka terminal dan jalankan server:

```bash
python http_server.py
```

Output yang akan muncul:
```
HTTP Chat Room Server berjalan di port 65432
Siap menerima koneksi dari 2 client!
Server berjalan sebagai relay (chat tidak ditampilkan di sini)
--------------------------------------------------
```

**Catatan Server:**
- Server berjalan di port `65432`
- Server berperan sebagai relay message (tidak menampilkan chat)
- Otomatis mengelola client dengan ID unik (`Client_1`, `Client_2`, dll)
- Menyimpan 10 pesan terakhir dalam memori

### 2. Menggunakan LocalTunnel (Opsional)

Jika server dan client berada di jaringan berbeda, gunakan LocalTunnel:

```bash
lt --port 65432
```

Output akan memberikan URL publik seperti:
```
your url is: https://abc123.loca.lt
```

### 3. Menjalankan HTTP Client

Buka terminal baru dan jalankan client:

```bash
python http_client.py
```

### 4. Konfigurasi Client

Program akan meminta URL server:

**Untuk koneksi lokal:**
```
Masukkan URL server LocalTunnel: localhost:65432
```

**Untuk koneksi via LocalTunnel:**
```
Masukkan URL server LocalTunnel: abc123.loca.lt
```

### 5. Bergabung ke Chat Room

Setelah terhubung, Anda akan menerima ID client:
```
Menghubungi server: https://abc123.loca.lt
Bergabung sebagai: Client_1
Chat Room dimulai! Ketik 'quit' untuk keluar
Anda akan melihat proses enkripsi/dekripsi DES
============================================================
```

### 6. Mengirim Pesan

Ketik pesan dan tekan Enter:
```
Ketik pesan Anda: Halo semua!
```

Program akan menampilkan proses enkripsi:
```
PROSES ENKRIPSI:
   Original    : Halo semua!
   Padded     : 'Halo semua!\x00\x00\x00\x00\x00'
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Encrypted  : dGVzdGVuY3J5cHRlZG1lc3NhZ2U=
--------------------------------------------------
Pesan terkirim dari Client_1!
```

### 7. Menerima Pesan

Ketika client lain mengirim pesan, Anda akan melihat proses dekripsi:
```
PROSES DEKRIPSI:
   Encrypted  : dGVzdGVuY3J5cHRlZG1lc3NhZ2U=
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Decrypted  : 'Halo juga!\x00\x00\x00\x00\x00\x00\x00'
   Original   : Halo juga!
--------------------------------------------------

Client_2: Halo juga!
Ketik pesan Anda: 
```

### 8. Keluar dari Chat

Ketik `quit` untuk keluar:
```
Ketik pesan Anda: quit
Client_1 keluar dari chat!
```

## Skenario Penggunaan Client 1 dan Client 2

### Persiapan Chat Room (2 Client)

Untuk menjalankan chat room dengan 2 client, ikuti langkah berikut:

#### **Terminal 1: Server**
```bash
# Jalankan server
python http_server.py
```
Output:
```
HTTP Chat Room Server berjalan di port 65432
Siap menerima koneksi dari 2 client!
Server berjalan sebagai relay (chat tidak ditampilkan di sini)
--------------------------------------------------
```

#### **Terminal 2: LocalTunnel (Opsional)**
Jika client dari jaringan berbeda:
```bash
lt --port 65432
```
Output:
```
your url is: https://abc123.loca.lt
```

### **Client 1 - Langkah Demi Langkah**

#### **Terminal 3: Client 1**
```bash
python http_client.py
```

**Step 1: Koneksi Client 1**
```
Masukkan URL server LocalTunnel: localhost:65432
# atau untuk external: abc123.loca.lt

Menghubungi server: http://localhost:65432
Bergabung sebagai: Client_1
Chat Room dimulai! Ketik 'quit' untuk keluar
Anda akan melihat proses enkripsi/dekripsi DES
============================================================
Ketik pesan Anda: 
```

**Step 2: Client 1 Mengirim Pesan Pertama**
```
Ketik pesan Anda: Halo, ada yang online?

PROSES ENKRIPSI:
   Original    : Halo, ada yang online?
   Padded     : 'Halo, ada yang online?\x00\x00\x00\x00\x00\x00\x00\x00\x00'
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Encrypted  : YWJjZGVmZ2hpamtsbW5vcA==
--------------------------------------------------
Pesan terkirim dari Client_1!
Ketik pesan Anda: 
```

### **Client 2 - Langkah Demi Langkah**

#### **Terminal 4: Client 2**
```bash
python http_client.py
```

**Step 1: Koneksi Client 2**
```
Masukkan URL server LocalTunnel: localhost:65432
# gunakan URL yang sama dengan Client 1

Menghubungi server: http://localhost:65432
Bergabung sebagai: Client_2
Chat Room dimulai! Ketik 'quit' untuk keluar
Anda akan melihat proses enkripsi/dekripsi DES
============================================================

# Client 2 langsung menerima pesan dari Client 1
PROSES DEKRIPSI:
   Encrypted  : YWJjZGVmZ2hpamtsbW5vcA==
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Decrypted  : 'Halo, ada yang online?\x00\x00\x00\x00\x00\x00\x00\x00\x00'
   Original   : Halo, ada yang online?
--------------------------------------------------

Client_1: Halo, ada yang online?
Ketik pesan Anda: 
```

**Step 2: Client 2 Membalas**
```
Ketik pesan Anda: Halo Client_1! Saya Client_2, sudah online

PROSES ENKRIPSI:
   Original    : Halo Client_1! Saya Client_2, sudah online
   Padded     : 'Halo Client_1! Saya Client_2, sudah online\x00\x00\x00\x00\x00\x00\x00'
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Encrypted  : cXdlcnR5dWlvcGFzZGZnaGprbA==
--------------------------------------------------
Pesan terkirim dari Client_2!
Ketik pesan Anda: 
```

### **Percakapan Berlanjut**

#### **Di Terminal Client 1:**
```
# Client 1 menerima balasan dari Client 2
PROSES DEKRIPSI:
   Encrypted  : cXdlcnR5dWlvcGFzZGZnaGprbA==
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Decrypted  : 'Halo Client_1! Saya Client_2, sudah online\x00\x00\x00\x00\x00\x00\x00'
   Original   : Halo Client_1! Saya Client_2, sudah online
--------------------------------------------------

Client_2: Halo Client_1! Saya Client_2, sudah online
Ketik pesan Anda: Bagus! Enkripsi DES bekerja dengan baik
```

#### **Di Terminal Client 2:**
```
# Client 2 menerima pesan lanjutan dari Client 1
PROSES DEKRIPSI:
   Encrypted  : emN2Ym5tdGVydHl1aW9wbHM=
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Decrypted  : 'Bagus! Enkripsi DES bekerja dengan baik\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
   Original   : Bagus! Enkripsi DES bekerja dengan baik
--------------------------------------------------

Client_1: Bagus! Enkripsi DES bekerja dengan baik
Ketik pesan Anda: 
```

### **Mengeluar Dari Chat**

#### **Client 1 Keluar Terlebih Dahulu:**
```
Ketik pesan Anda: quit
Client_1 keluar dari chat!
```

#### **Client 2 Melihat Client 1 Keluar:**
```
# Client 2 masih bisa mengirim pesan
Ketik pesan Anda: Client_1 sudah keluar, saya juga keluar ya

PROSES ENKRIPSI:
   Original    : Client_1 sudah keluar, saya juga keluar ya
   Padded     : 'Client_1 sudah keluar, saya juga keluar ya\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
   DES Key    : b'8bytekey'
   Block Size : 64-bit
   Rounds     : 16
   Encrypted  : bm5sb2tzZGZnanJld3F0eXVp
--------------------------------------------------
Pesan terkirim dari Client_2!
Ketik pesan Anda: quit
Client_2 keluar dari chat!
```

### **Tips untuk Multiple Client:**

1. **URL yang Sama**: Pastikan semua client menggunakan URL server yang sama
2. **Urutan Join**: Client bisa join kapan saja, tidak harus bersamaan
3. **History Pesan**: Client baru akan melihat 10 pesan terakhir
4. **ID Otomatis**: Server otomatis memberikan ID unik (Client_1, Client_2, dst)
5. **Pesan Sendiri**: Client tidak akan menerima pesan yang mereka kirim sendiri

### **Troubleshooting Multi-Client:**

**Jika Client 2 tidak menerima pesan Client 1:**
1. Pastikan Client 1 sudah mengirim pesan sebelum Client 2 join
2. Tunggu 2-3 detik (polling interval)
3. Restart Client 2 jika masalah berlanjut

**Jika ada konflik ID client:**
1. Restart server untuk reset ID counter
2. Pastikan client lama sudah keluar dengan 'quit'

## Detail Implementasi

### Algoritma DES
- **Kunci**: `b'8bytekey'` (8 bytes, sesuai standar DES)
- **Mode**: ECB (Electronic Codebook)
- **Padding**: Null bytes (`\x00`) sampai kelipatan 8 bytes
- **Encoding**: Base64 untuk transmisi HTTP

### HTTP Endpoints
Server menerima POST request dengan action:
- `join`: Bergabung ke chat room
- `send_message`: Mengirim pesan terenkripsi
- `get_messages`: Mengambil pesan dari client lain
- `quit`: Keluar dari chat room

### Keamanan
- Semua pesan dienkripsi menggunakan DES sebelum dikirim
- Kunci enkripsi tersimpan di kedua sisi (server dan client)
- Pesan ditransmisikan dalam format Base64

## Troubleshooting

### Server tidak bisa diakses
1. Pastikan server berjalan di port yang benar
2. Periksa firewall/antivirus yang mungkin memblokir port
3. Gunakan LocalTunnel untuk akses eksternal

### Client tidak bisa terhubung
1. Periksa URL server yang dimasukkan
2. Pastikan koneksi internet stabil
3. Coba gunakan format URL yang berbeda (dengan/tanpa https)

### Pesan tidak muncul
1. Pastikan client lain sudah mengirim pesan
2. Tunggu beberapa detik (polling interval 2 detik)
3. Restart client jika masalah berlanjut

## Struktur Kode

### HTTP Server (`http_server.py`)
- Mengelola koneksi multiple client
- Mengimplementasi enkripsi/dekripsi DES
- Menyimpan pesan sementara dalam memori
- Memberikan response JSON untuk setiap request

### HTTP Client (`http_client.py`)
- Interface untuk user input
- Thread terpisah untuk listening pesan
- Menampilkan proses enkripsi/dekripsi secara detail
- Mengelola lifecycle connection ke server

## Catatan Penting

1. **Kunci DES**: Kunci saat ini adalah `8bytekey`. Untuk keamanan lebih baik, ganti dengan kunci yang lebih kompleks.

2. **Kapasitas**: Server dapat menangani multiple client, tapi disarankan maksimal 10 client bersamaan.

3. **Persistensi**: Pesan tidak disimpan secara permanen. Restart server akan menghapus semua pesan.

4. **Enkripsi**: DES adalah algoritma lama. Untuk aplikasi production, gunakan AES atau algoritma modern lainnya.
