# Tugas 3: Public Key Distribution of Secret Keys

**Mata Kuliah**: Keamanan Informasi  
**Kelas**: C

## Tim Pengembang

| Nama | NRP |
|------|-----|
| Muhammad Danis Hadriansyah | 5025221239 |
| Fathurazka Gamma Syuhada | 5025231246 |

## Deskripsi

Implementasi sistem chat terenkripsi menggunakan **Diffie-Hellman Key Exchange** untuk distribusi secret key DES secara aman. Kedua pihak tidak perlu mengetahui secret key sebelumnya - key di-generate otomatis melalui protokol DH.

## Cara Kerja Sistem

### 1. Diffie-Hellman Key Exchange

```
Server:                 Client:
Private: b (fixed)      Private: a (random)
Public: B = g^b mod p   Public: A = g^a mod p

Exchange → Shared Secret = g^(ab) mod p
DES Key = SHA256(shared_secret)[:8]
```

**Parameter:**
- Prime: 2048-bit safe prime
- Generator: 2
- Private key client: random (persistent di file)

**Keamanan:**
- Attacker tidak bisa hitung shared secret dari public keys (Discrete Log Problem)
- Secret key tidak pernah dikirim via network

### 2. Enkripsi DES

**Implementasi:**
- 16 rounds, 48-bit subkeys
- 64-bit block cipher
- Padding ke kelipatan 8 bytes
- Base64 encoding untuk transport

### 3. Chat Architecture

**Server:**
- Simpan shared secret per client
- Terima pesan encrypted dari sender
- Dekripsi dengan sender key
- Re-encrypt untuk setiap recipient dengan key mereka
- Broadcast ke semua client

**Client:**
- Persistent private key (di file)
- Enkripsi pesan sebelum kirim
- Dekripsi pesan yang diterima
- Polling server setiap 2 detik

## Komponen Program

**http_server.py:**
- DH key exchange endpoints
- DES encryption/decryption
- Chat room management (max 100 pesan)
- Re-encryption untuk multi-client
- Endpoints: `get_server_public_key`, `exchange_key`, `send_message`, `get_messages`, `join`, `quit`

**http_client.py:**
- DH key exchange dengan server
- DES encryption/decryption
- Key persistence (`.client_[name]_private_key.txt`)
- Threading untuk polling pesan
- Chat interface

## Cara Menjalankan

### 1. Persiapan

```bash
pip install requests
```

### 2. Jalankan Server

Terminal 1:
```bash
python http_server.py
```

Output:
```
==================================================
SECURE CHAT SERVER (Diffie-Hellman + DES)
==================================================
Port: 65432
Server Public Key: 1234567890...
==================================================
```

### 3. Jalankan Client

Terminal 2:
```bash
python http_client.py
```

Input:
```
Server URL: localhost:65432
```

Output:
```
Bergabung sebagai: Client_1

=== DIFFIE-HELLMAN KEY EXCHANGE ===
Menerima parameter DH dari server
Generate private key baru (disimpan)
Key exchange dengan server berhasil
DES Key: a1b2c3d4e5f6a7b8
========================================

Chat aktif! Ketik 'quit' untuk keluar

>>> 
```

### 4. Client Kedua (Opsional)

Terminal 3:
```bash
python http_client.py
# Input: localhost:65432
```

### 5. Mulai Chat

**Client_1:**
```
>>> Halo!
```

**Client_2 menerima:**
```
Client_1: Halo!
>>> 
```

**Client_2 balas:**
```
>>> Halo juga!
```

### 6. Keluar

```
>>> quit
Client_1 keluar dari chat
```

## Fitur Khusus

### Key Persistence

Private key disimpan di file `.client_[name]_private_key.txt`:
- Rejoin menggunakan key yang sama
- Shared secret tetap konsisten
- Tidak perlu re-exchange setiap restart

### Message Clearing

Saat client rejoin:
- Pesan lama untuk client tersebut otomatis dihapus
- Hindari dekripsi gagal (key mismatch)
- Client mulai dengan history bersih

### Re-encryption

Server otomatis re-encrypt pesan:
- Dekripsi dengan key sender
- Re-encrypt untuk setiap recipient dengan key mereka
- Setiap client punya DES key unik

## Troubleshooting

**Connection reset saat rejoin:**
- Sudah diperbaiki: server retain key saat client quit
- Pesan lama di-clear otomatis saat rejoin

**Pesan jadi sampah (garbled text):**
- Sudah diperbaiki: pesan lama dihapus saat key exchange
- Tidak ada lagi pesan terenkripsi dengan key lama

**Key mismatch:**
- Hapus file `.client_*_private_key.txt`
- Restart client untuk generate key baru

**Server tidak bisa diakses:**
- Pastikan port 65432 tidak dipakai
- Cek firewall
- Gunakan LocalTunnel untuk akses eksternal:
  ```bash
  npm install -g localtunnel
  lt --port 65432
  ```

## Algoritma & Keamanan

| Komponen | Detail |
|----------|--------|
| Key Exchange | Diffie-Hellman 2048-bit |
| Encryption | DES 56-bit |
| Key Derivation | SHA-256 |
| Encoding | Base64 |
| Transport | HTTP POST JSON |

**Catatan Keamanan:**
- Implementasi edukatif untuk memahami konsep
- Untuk production gunakan AES-256 (bukan DES)
- Tambahkan authentication (digital signature)
- Gunakan HTTPS (bukan HTTP)

---

*Keamanan Informasi - Kelas C - 2025*