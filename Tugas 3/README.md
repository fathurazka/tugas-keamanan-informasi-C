# Tugas 3: Public Key Distribution of Secret Keys

**Mata Kuliah**: Keamanan Informasi  
**Kelas**: C

## Tim Pengembang

| Nama | NRP |
|------|-----|
| Muhammad Danis Hadriansyah | 5025221239 |
| Fathurazka Gamma Syuhada | 5025221128 |

## Deskripsi

Sistem chat sederhana dengan kriptografi hybrid: **RSA** untuk mendistribusikan kunci simetris, dan **DES** untuk mengenkripsi pesan chat. RSA hanya dipakai saat key exchange; seluruh pesan setelahnya dienkripsi dengan DES.

## Cara Kerja (ringkas)

1) **Server** membuat pasangan kunci RSA (1024-bit) saat startup.  
2) **Client** meminta RSA public key server.  
3) **Client** membuat kunci DES acak 8 byte (disimpan di file lokal).  
4) Kunci DES di-enkripsi dengan RSA public key server, dikirim ke server.  
5) Server mendekripsi memakai RSA private key, menyimpan kunci DES per `client_name`.  
6) Chat: client mengenkripsi pesan dengan DES; server mendekripsi memakai kunci pengirim, lalu re-encrypt untuk tiap penerima dengan kunci DES mereka.  
7) Riwayat pesan dibatasi 100 item; client polling setiap 2 detik.

## Komponen Program

**http_server.py**
- Generate RSA keypair (1024-bit) saat start.
- Endpoint:
  - `get_server_public_key` → kirim `(e, n)` RSA.
  - `exchange_key` → terima DES key terenkripsi RSA; simpan per client.
  - `join` / `quit` → registrasi nama otomatis `Client_X`.
  - `send_message` → terima ciphertext DES, decrypt, re-encrypt ke semua penerima lain.
  - `get_messages` → kirim pesan yang ditujukan ke client peminta.
- Menyimpan kunci DES per client di `client_des_keys` dan buffer `recent_messages` (maks 100).

**http_client.py**
- Meminta public key RSA server, generate/ambil kunci DES 8 byte.
- Enkripsi kunci DES dengan RSA, kirim ke server (`exchange_key`).
- Enkripsi/dekripsi pesan chat memakai DES (implementasi manual tabel S-Box, dsb).
- Polling pesan setiap 2 detik di thread terpisah.
- Persistensi kunci: file `.client_<nama>_des_key.bin` (dibuat sekali, dipakai ulang).

## Cara Menjalankan

### 1) Persiapan

```bash
pip install requests
```

### 2) Jalankan Server

Terminal 1:

```bash
python http_server.py
```

Output ringkas yang terlihat:

```
============================================================
SECURE CHAT SERVER (RSA + DES)
============================================================
Port: 65432
RSA Public Key (e): 65537
RSA Public Key (n): <n dipotong>
Server siap menerima koneksi...
```

### 3) Jalankan Client

Terminal 2:

```bash
python http_client.py
```

Input saat diminta URL:

```
Masukkan Server URL: http://localhost:65432
```

Alur yang terjadi di client:
- Join: otomatis mendapat nama `Client_X`.
- RSA key exchange: ambil public key, generate/ambil DES key (persisten), enkripsi DES key dengan RSA, kirim ke server.
- Mulai chat: ketik pesan biasa; ketik `quit` untuk keluar.

### 4) Client lain (opsional)

Jalankan perintah yang sama di terminal berbeda, masukkan URL server yang sama. Tiap client mendapat kunci DES unik.

## Alur Pesan

1) Pengirim mengenkripsi plaintext dengan DES → ciphertext dikirim ke server.  
2) Server mendekripsi ciphertext dengan kunci DES pengirim.  
3) Server mengenkripsi ulang plaintext untuk tiap penerima dengan kunci DES mereka.  
4) Penerima mem-poll `get_messages`, lalu mendekripsi ciphertext dengan kunci DES miliknya.

## Cuplikan Kode RSA & DES

### Server (http_server.py)

**1. Generate RSA keypair saat start:**
```python
def generate_rsa_keypair(bits=1024):
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while gcd(e, phi) != 1:
        e = secrets.randbelow(phi - 2) + 2
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

# Generate keypair
server_public_key, server_private_key = generate_rsa_keypair(1024)
```

**2. Kirim public key ke client:**
```python
if action == 'get_server_public_key':
    e, n = server_public_key
    response = {
        'status': 'success',
        'e': str(e),
        'n': str(n)
    }
```

**3. Terima DES key terenkripsi RSA, decrypt, simpan:**
```python
elif action == 'exchange_key':
    client_name = data.get('client_name', 'Unknown')
    encrypted_des_key = int(data.get('encrypted_des_key'))
    
    # Decrypt the DES key using server's private key
    des_key_int = rsa_decrypt(encrypted_des_key, server_private_key)
    
    # Convert integer back to 8-byte key
    des_key = des_key_int.to_bytes(8, 'big')
    
    client_des_keys[client_name] = des_key
    print(f"[KEY] {client_name}: received DES key {des_key.hex()}")
    
    # Clear old messages for this client
    recent_messages[:] = [msg for msg in recent_messages 
                         if msg.get('recipient') != client_name]
```

**4. Terima pesan, decrypt dengan kunci pengirim, re-encrypt untuk setiap penerima:**
```python
elif action == 'send_message':
    encrypted_msg = data['message']
    client_name = data.get('client_name', 'Unknown')
    
    if client_name in client_des_keys:
        sender_key = client_des_keys[client_name]
        plaintext = decrypt_message(encrypted_msg, sender_key)
        print(f"[CHAT] {client_name}: {plaintext}")
        
        # Re-encrypt for each recipient with their own key
        for recipient_name, recipient_key in client_des_keys.items():
            if recipient_name != client_name:
                re_encrypted = encrypt_message(plaintext, recipient_key)
                message_data = {
                    'message': re_encrypted,
                    'sender': client_name,
                    'recipient': recipient_name,
                    'timestamp': time.time()
                }
                recent_messages.append(message_data)
```

**5. Fungsi DES enkripsi/dekripsi di server:**
```python
def encrypt_message(message, key):
    subkeys = generate_subkeys(key)
    padded_message = message.ljust((len(message) + 7) // 8 * 8, '\x00')
    encrypted_blocks = []
    for i in range(0, len(padded_message), 8):
        block = padded_message[i:i+8]
        block_bin = string_to_binary(block)
        encrypted_block = des_encrypt_block(block_bin, subkeys)
        encrypted_blocks.append(binary_to_string(encrypted_block))
    encrypted_message = ''.join(encrypted_blocks)
    return base64.b64encode(encrypted_message.encode('latin-1')).decode('utf-8')
```

### Client (http_client.py)

**1. RSA encrypt function:**
```python
def rsa_encrypt(message, public_key):
    e, n = public_key
    return pow(message, e, n)
```

**2. Key exchange dengan server:**
```python
def perform_key_exchange(server_url, my_name):
    global SHARED_DES_KEY
    
    # Get server's public key
    response = requests.post(server_url, 
        json={'action': 'get_server_public_key'}, 
        timeout=30)
    
    data = response.json()
    e = int(data['e'])
    n = int(data['n'])
    server_public_key = (e, n)
    
    print("Menerima RSA public key dari server")
    
    # Load or generate DES key
    key_file = f'.client_{my_name}_des_key.bin'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            SHARED_DES_KEY = f.read()
        print(f"Load DES key dari file (persistent)")
    else:
        # Generate random 8-byte DES key
        SHARED_DES_KEY = secrets.token_bytes(8)
        with open(key_file, 'wb') as f:
            f.write(SHARED_DES_KEY)
        print(f"Generate DES key baru (disimpan)")
    
    print(f"DES Key: {SHARED_DES_KEY.hex()}")
    
    # Convert DES key to integer for RSA encryption
    des_key_int = int.from_bytes(SHARED_DES_KEY, 'big')
    
    # Encrypt DES key with server's RSA public key
    encrypted_des_key = rsa_encrypt(des_key_int, server_public_key)
    
    # Send encrypted DES key to server
    response = requests.post(server_url,
        json={
            'action': 'exchange_key',
            'client_name': my_name,
            'encrypted_des_key': str(encrypted_des_key)
        },
        timeout=30)
```

**3. Enkripsi pesan dengan DES sebelum kirim:**
```python
def encrypt_message(message):
    subkeys = generate_subkeys(SHARED_DES_KEY)
    padded_message = message.ljust((len(message) + 7) // 8 * 8, '\x00')
    encrypted_blocks = []
    for i in range(0, len(padded_message), 8):
        block = padded_message[i:i+8]
        block_bin = string_to_binary(block)
        encrypted_block = des_encrypt_block(block_bin, subkeys)
        encrypted_blocks.append(binary_to_string(encrypted_block))
    encrypted_message = ''.join(encrypted_blocks)
    return base64.b64encode(encrypted_message.encode('latin-1')).decode('utf-8')

# Kirim pesan
encrypted_message = encrypt_message(message)
response = requests.post(server_url, 
    json={
        'action': 'send_message',
        'message': encrypted_message,
        'client_name': my_name
    }, 
    timeout=30)
```

**4. Terima dan dekripsi pesan:**
```python
def listen_for_messages(server_url, my_name):
    last_message_count = 0
    
    while True:
        response = requests.post(server_url, 
            json={
                'action': 'get_messages',
                'client_name': my_name
            }, 
            timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and data['messages']:
                new_messages = data['messages'][last_message_count:]
                for msg in new_messages:
                    sender = msg['sender']
                    encrypted_msg = msg['message']
                    try:
                        decrypted_msg = decrypt_message(encrypted_msg)
                        print(f"\n{sender}: {decrypted_msg}")
                    except:
                        print(f"\n{sender}: [dekripsi gagal]")
                
                last_message_count = len(data['messages'])
        
        time.sleep(2)
```

## Troubleshooting

- **Key mismatch / pesan garbled**: hapus file `.client_*_des_key.bin`, lalu jalankan client lagi untuk regenerasi kunci.
- **Timeout/koneksi gagal**: pastikan server jalan di port 65432, cek firewall, coba `http://localhost:65432` di mesin yang sama.
- **Pesan tidak muncul**: pastikan kedua client sudah sukses key exchange (lihat log server ada `[KEY] <client>: received DES key ...`).

## Catatan Keamanan

- RSA 1024-bit dan DES 56-bit hanya untuk tujuan edukasi; tidak aman untuk produksi.
- Gunakan HTTPS untuk melindungi transport; tambahkan autentikasi/ tanda tangan digital jika dipakai serius.
- Untuk praktik nyata: ganti DES dengan AES-256 dan gunakan RSA 2048/3072 atau ECDH/ECDSA.

---

*Keamanan Informasi - Kelas C - 2025*
