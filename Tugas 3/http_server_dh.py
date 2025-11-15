import http.server
import socketserver
import json
import threading
import queue
import time
import base64
import hashlib

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

# ==================== DIFFIE-HELLMAN IMPLEMENTATION ====================
# Parameter publik Diffie-Hellman (bilangan prima besar dan generator)
DH_PRIME = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
DH_GENERATOR = 2

# Private key server (rahasia)
server_private_key = 123456789012345  # Dalam implementasi nyata, gunakan random number

# Public key server (dihitung dari private key)
def mod_exp(base, exp, mod):
    """Modular exponentiation: (base^exp) % mod"""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

server_public_key = mod_exp(DH_GENERATOR, server_private_key, DH_PRIME)

# Storage untuk shared secrets setiap client
client_shared_secrets = {}

def derive_des_key(shared_secret):
    """Convert shared secret ke 8-byte DES key menggunakan SHA-256"""
    secret_bytes = str(shared_secret).encode('utf-8')
    hash_digest = hashlib.sha256(secret_bytes).digest()
    return hash_digest[:8]  # Ambil 8 byte pertama untuk DES key

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
    return base64.b64encode(encrypted_message.encode('utf-8')).decode('utf-8')

def decrypt_message(encrypted_message, key):
    subkeys = generate_subkeys(key)
    encrypted_binary = base64.b64decode(encrypted_message).decode('utf-8')
    decrypted_blocks = []
    for i in range(0, len(encrypted_binary), 8):
        block = encrypted_binary[i:i+8]
        block_bin = string_to_binary(block)
        decrypted_block = des_decrypt_block(block_bin, subkeys)
        decrypted_blocks.append(binary_to_string(decrypted_block))
    decrypted_message = ''.join(decrypted_blocks)
    return decrypted_message.rstrip('\x00')

# ==================== CHAT ROOM ====================
chat_room = queue.Queue()
active_clients = set()
recent_messages = []

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            action = data.get('action')
            
            # ==================== DIFFIE-HELLMAN KEY EXCHANGE ====================
            if action == 'get_server_public_key':
                # Client meminta public key server
                response = {
                    'status': 'success',
                    'server_public_key': str(server_public_key),
                    'dh_prime': str(DH_PRIME),
                    'dh_generator': str(DH_GENERATOR)
                }
                print(f"\n[DH] Server mengirim public key ke client")
                
            elif action == 'exchange_key':
                # Client mengirim public key-nya, server hitung shared secret
                client_name = data.get('client_name', 'Unknown')
                client_public_key = int(data.get('client_public_key'))
                
                # Hitung shared secret: (client_public_key ^ server_private_key) mod prime
                shared_secret = mod_exp(client_public_key, server_private_key, DH_PRIME)
                
                # Derive DES key dari shared secret
                des_key = derive_des_key(shared_secret)
                client_shared_secrets[client_name] = des_key
                
                print(f"\n[DH] Key exchange dengan {client_name}")
                print(f"     Client Public Key: {client_public_key}")
                print(f"     Shared Secret (hash): {hashlib.sha256(str(shared_secret).encode()).hexdigest()[:16]}...")
                print(f"     DES Key: {des_key.hex()}")
                
                response = {
                    'status': 'success',
                    'message': 'Key exchange completed'
                }
            
            # ==================== CHAT OPERATIONS ====================
            elif action == 'send_message':
                encrypted_msg = data['message']
                client_name = data.get('client_name', 'Unknown')
                
                # Decrypt untuk logging di server (opsional)
                if client_name in client_shared_secrets:
                    try:
                        des_key = client_shared_secrets[client_name]
                        decrypted = decrypt_message(encrypted_msg, des_key)
                        print(f"\n[CHAT] {client_name}: {decrypted}")
                    except:
                        print(f"\n[CHAT] {client_name}: <encrypted message>")
                
                message_data = {
                    'message': encrypted_msg,
                    'sender': client_name,
                    'timestamp': time.time()
                }
                recent_messages.append(message_data)
                
                if len(recent_messages) > 50:
                    recent_messages.pop(0)
                
                response = {'status': 'sent'}
                
            elif action == 'get_messages':
                client_name = data.get('client_name', '')
                messages = [msg for msg in recent_messages if msg['sender'] != client_name]
                response = {
                    'status': 'success',
                    'messages': messages
                }
                
            elif action == 'join':
                client_num = 1
                while client_num in active_clients:
                    client_num += 1
                active_clients.add(client_num)
                client_name = f"Client_{client_num}"
                
                response = {
                    'status': 'joined',
                    'client_name': client_name
                }
                print(f"\n[JOIN] {client_name} bergabung ke chat room")
                
            elif action == 'quit':
                client_name = data.get('client_name', '')
                if client_name.startswith('Client_'):
                    try:
                        client_num = int(client_name.split('_')[1])
                        active_clients.discard(client_num)
                        if client_name in client_shared_secrets:
                            del client_shared_secrets[client_name]
                    except ValueError:
                        pass
                response = {'status': 'quit'}
                print(f"\n[QUIT] {client_name} keluar dari chat room")
                
            else:
                response = {'status': 'connected'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

PORT = 65432
print("=" * 70)
print("HTTP CHAT ROOM SERVER WITH DIFFIE-HELLMAN KEY EXCHANGE")
print("=" * 70)
print(f"Server berjalan di port {PORT}")
print(f"Server Public Key: {str(server_public_key)[:50]}...")
print(f"DH Prime: {str(DH_PRIME)[:50]}...")
print(f"DH Generator: {DH_GENERATOR}")
print("-" * 70)
print("Menunggu client untuk key exchange dan chat...")
print("=" * 70)

with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
    httpd.serve_forever()