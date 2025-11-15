import requests
import json
import time
import threading
import base64
import hashlib
import secrets

# DES Tables (sama seperti sebelumnya)
IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]

FP = [40, 8, 48, 16, 56, 24, 64, 32,
      39, 7, 47, 15, 55, 23, 63, 31,
      38, 6, 46, 14, 54, 22, 62, 30,
      37, 5, 45, 13, 53, 21, 61, 29,
      36, 4, 44, 12, 52, 20, 60, 28,
      35, 3, 43, 11, 51, 19, 59, 27,
      34, 2, 42, 10, 50, 18, 58, 26,
      33, 1, 41, 9, 49, 17, 57, 25]

E = [32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32, 1]

S_BOX = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],

    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],

    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],

    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],

    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],

    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],

    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]

P = [16, 7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26, 5, 18, 31, 10,
     2, 8, 24, 14, 32, 27, 3, 9,
     19, 13, 30, 6, 22, 11, 4, 25]

PC1 = [57, 49, 41, 33, 25, 17, 9,
       1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27,
       19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
       7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29,
       21, 13, 5, 28, 20, 12, 4]

PC2 = [14, 17, 11, 24, 1, 5,
       3, 28, 15, 6, 21, 10,
       23, 19, 12, 4, 26, 8,
       16, 7, 27, 20, 13, 2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

SHIFT = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Global variable untuk menyimpan shared key setelah key exchange
SHARED_DES_KEY = None

# ==================== DIFFIE-HELLMAN IMPLEMENTATION ====================
def mod_exp(base, exp, mod):
    """Modular exponentiation: (base^exp) % mod - konvensional"""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

def derive_des_key(shared_secret):
    """Convert shared secret ke 8-byte DES key menggunakan SHA-256"""
    secret_bytes = str(shared_secret).encode('utf-8')
    hash_digest = hashlib.sha256(secret_bytes).digest()
    return hash_digest[:8]  # Ambil 8 byte pertama untuk DES key

def perform_key_exchange(server_url, my_name):
    """Melakukan Diffie-Hellman key exchange dengan server"""
    global SHARED_DES_KEY
    
    print("\n" + "=" * 70)
    print("DIFFIE-HELLMAN KEY EXCHANGE")
    print("=" * 70)
    
    try:
        # 1. Minta public key dari server
        print("[1] Meminta parameter DH dari server...")
        response = requests.post(server_url, 
            json={'action': 'get_server_public_key'}, 
            timeout=10)
        
        if response.status_code != 200:
            print("Gagal mendapatkan server public key")
            return False
        
        data = response.json()
        server_public_key = int(data['server_public_key'])
        dh_prime = int(data['dh_prime'])
        dh_generator = int(data['dh_generator'])
        
        print(f"    ✓ Server Public Key: {str(server_public_key)[:50]}...")
        print(f"    ✓ DH Prime (p): {str(dh_prime)[:50]}...")
        print(f"    ✓ DH Generator (g): {dh_generator}")
        
        # 2. Generate private key client (random)
        print("\n[2] Generate private key client...")
        # Gunakan secrets untuk cryptographic random number
        client_private_key = secrets.randbelow(dh_prime - 2) + 1
        print(f"    ✓ Client Private Key: {str(client_private_key)[:50]}... (RAHASIA)")
        
        # 3. Hitung public key client: g^a mod p
        print("\n[3] Menghitung public key client...")
        client_public_key = mod_exp(dh_generator, client_private_key, dh_prime)
        print(f"    ✓ Client Public Key: {str(client_public_key)[:50]}...")
        
        # 4. Kirim public key client ke server
        print("\n[4] Mengirim public key ke server...")
        response = requests.post(server_url,
            json={
                'action': 'exchange_key',
                'client_name': my_name,
                'client_public_key': str(client_public_key)
            },
            timeout=10)
        
        if response.status_code != 200:
            print("Gagal mengirim public key")
            return False
        
        print("    ✓ Public key terkirim ke server")
        
        # 5. Hitung shared secret: (server_public_key^client_private_key) mod prime
        print("\n[5] Menghitung shared secret...")
        shared_secret = mod_exp(server_public_key, client_private_key, dh_prime)
        print(f"    ✓ Shared Secret: {str(shared_secret)[:50]}...")
        
        # 6. Derive DES key dari shared secret
        print("\n[6] Membuat DES key dari shared secret...")
        SHARED_DES_KEY = derive_des_key(shared_secret)
        print(f"    ✓ DES Key (8 bytes): {SHARED_DES_KEY.hex()}")
        
        print("\n" + "=" * 70)
        print("KEY EXCHANGE BERHASIL!")
        print("=" * 70)
        print(f"Shared Secret Hash: {hashlib.sha256(str(shared_secret).encode()).hexdigest()[:32]}...")
        print(f"DES Key yang akan digunakan: {SHARED_DES_KEY.hex()}")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"Error during key exchange: {e}")
        return False

# ==================== DES FUNCTIONS ====================
def permute(block, table):
    return ''.join(block[i - 1] for i in table)

def string_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def binary_to_string(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def xor(a, b):
    return ''.join('1' if x != y else '0' for x, y in zip(a, b))

def generate_subkeys(key):
    key_bin = string_to_binary(key.decode())
    key_pc1 = permute(key_bin, PC1)
    c = key_pc1[:28]
    d = key_pc1[28:]
    subkeys = []
    for i in range(16):
        c = left_shift(c, SHIFT[i])
        d = left_shift(d, SHIFT[i])
        subkey = permute(c + d, PC2)
        subkeys.append(subkey)
    return subkeys

def f_function(right, subkey):
    expanded = permute(right, E)
    xor_result = xor(expanded, subkey)
    s_box_output = ''
    for i in range(8):
        block = xor_result[i*6:(i+1)*6]
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        s_box_value = S_BOX[i][row][col]
        s_box_output += format(s_box_value, '04b')
    return permute(s_box_output, P)

def des_round(left, right, subkey):
    new_left = right
    new_right = xor(left, f_function(right, subkey))
    return new_left, new_right

def des_encrypt_block(block, subkeys):
    block = permute(block, IP)
    left = block[:32]
    right = block[32:]
    for i in range(16):
        left, right = des_round(left, right, subkeys[i])
    return permute(right + left, FP)

def des_decrypt_block(block, subkeys):
    block = permute(block, IP)
    left = block[:32]
    right = block[32:]
    for i in range(15, -1, -1):
        left, right = des_round(left, right, subkeys[i])
    return permute(right + left, FP)

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
    encrypted_base64 = base64.b64encode(encrypted_message.encode('utf-8')).decode('utf-8')
    
    print(f"\n[ENKRIPSI]")
    print(f"  Plaintext : {message}")
    print(f"  DES Key   : {SHARED_DES_KEY.hex()}")
    print(f"  Encrypted : {encrypted_base64[:50]}...")
    print("-" * 70)
    
    return encrypted_base64

def decrypt_message(encrypted_message):
    subkeys = generate_subkeys(SHARED_DES_KEY)
    encrypted_binary = base64.b64decode(encrypted_message).decode('utf-8')
    decrypted_blocks = []
    for i in range(0, len(encrypted_binary), 8):
        block = encrypted_binary[i:i+8]
        block_bin = string_to_binary(block)
        decrypted_block = des_decrypt_block(block_bin, subkeys)
        decrypted_blocks.append(binary_to_string(decrypted_block))
    decrypted_message = ''.join(decrypted_blocks)
    original_message = decrypted_message.rstrip('\x00')
    
    print(f"\n[DEKRIPSI]")
    print(f"  Encrypted : {encrypted_message[:50]}...")
    print(f"  DES Key   : {SHARED_DES_KEY.hex()}")
    print(f"  Plaintext : {original_message}")
    print("-" * 70)
    
    return original_message

def listen_for_messages(server_url, my_name):
    """Thread untuk mendengarkan pesan dari client lain"""
    last_message_count = 0
    
    while True:
        try:
            response = requests.post(server_url, 
                json={
                    'action': 'get_messages',
                    'client_name': my_name
                }, 
                timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['messages']:
                    new_messages = data['messages'][last_message_count:]
                    for msg in new_messages:
                        sender = msg['sender']
                        encrypted_msg = msg['message']
                        decrypted_msg = decrypt_message(encrypted_msg)
                        print(f"\n💬 {sender}: {decrypted_msg}")
                        print("Ketik pesan Anda: ", end="", flush=True)
                    
                    last_message_count = len(data['messages'])
            
            time.sleep(2)
            
        except requests.RequestException:
            time.sleep(5)
        except KeyboardInterrupt:
            break

def main():
    global SHARED_DES_KEY
    
    print("=" * 70)
    print("SECURE CHAT CLIENT WITH DIFFIE-HELLMAN KEY EXCHANGE")
    print("=" * 70)
    
    server_url = input("Masukkan URL server LocalTunnel: ")
    if not server_url.startswith('http'):
        server_url = 'https://' + server_url
    
    print(f"\nMenghubungi server: {server_url}")
    
    # Join chat room
    try:
        response = requests.post(server_url, json={'action': 'join'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            my_name = data['client_name']
            print(f"✓ Bergabung sebagai: {my_name}")
        else:
            print("✗ Tidak bisa join chat room")
            return
    except:
        print("✗ Tidak bisa terhubung ke server")
        return
    
    # Perform Diffie-Hellman key exchange
    if not perform_key_exchange(server_url, my_name):
        print("✗ Key exchange gagal. Keluar dari program.")
        return
    
    # Start listening thread
    listen_thread = threading.Thread(target=listen_for_messages, args=(server_url, my_name), daemon=True)
    listen_thread.start()
    
    print("\n" + "=" * 70)
    print("CHAT ROOM AKTIF - Komunikasi Terenkripsi DES")
    print("=" * 70)
    print("Ketik pesan Anda dan tekan Enter untuk mengirim")
    print("Ketik 'quit' untuk keluar")
    print("=" * 70 + "\n")
    
    try:
        while True:
            message = input("Ketik pesan Anda: ")
            if message.lower() == 'quit':
                try:
                    response = requests.post(server_url,
                        json={
                            'action': 'quit',
                            'client_name': my_name
                        },
                        timeout=10)
                    if response.status_code == 200:
                        print(f"\n{my_name} keluar dari chat!")
                    else:
                        print("Gagal mengirim sinyal quit")
                except:
                    print("Gagal mengirim sinyal quit")
                break
            
            if not message.strip():
                continue
            
            encrypted_message = encrypt_message(message)
            
            try:
                response = requests.post(server_url, 
                    json={
                        'action': 'send_message',
                        'message': encrypted_message,
                        'client_name': my_name
                    }, 
                    timeout=10)
                
                if response.status_code == 200:
                    print(f"✓ Pesan terkirim dari {my_name}!")
                else:
                    print("✗ Gagal mengirim pesan")
                    
            except requests.RequestException as e:
                print(f"Error: {e}")
                
    except KeyboardInterrupt:
        try:
            response = requests.post(server_url,
                json={
                    'action': 'quit',
                    'client_name': my_name
                },
                timeout=10)
        except:
            pass
        print(f"\n{my_name} keluar dari chat!")

if __name__ == "__main__":
    main()