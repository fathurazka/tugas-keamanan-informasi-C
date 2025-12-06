import http.server
import socketserver
import json
import time
import base64
import hashlib
import secrets
import sys

# DES Tables
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

# ==================== RSA FUNCTIONS ====================
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y
    
    _, x, _ = extended_gcd(e % phi, phi)
    return (x % phi + phi) % phi

def is_prime(n, k=5):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=512):
    while True:
        num = secrets.randbits(bits)
        num |= (1 << bits - 1) | 1
        if is_prime(num):
            return num

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

def rsa_encrypt(message, public_key):
    e, n = public_key
    return pow(message, e, n)

def rsa_decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)

# Generate RSA keypair for server
print("Generating RSA keypair...")
server_public_key, server_private_key = generate_rsa_keypair(1024)
print("RSA keypair generated!")

client_des_keys = {}

# ==================== DES FUNCTIONS ====================
def permute(block, table):
    return ''.join(block[i - 1] for i in table)

def string_to_binary(text):
    if isinstance(text, bytes):
        return ''.join(format(byte, '08b') for byte in text)
    else:
        return ''.join(format(ord(c), '08b') for c in text)

def binary_to_string(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def xor(a, b):
    return ''.join('1' if x != y else '0' for x, y in zip(a, b))

def generate_subkeys(key):
    if isinstance(key, bytes):
        key_bin = string_to_binary(key)
    else:
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
    return base64.b64encode(encrypted_message.encode('latin-1')).decode('utf-8')

def decrypt_message(encrypted_message, key):
    subkeys = generate_subkeys(key)
    encrypted_binary = base64.b64decode(encrypted_message).decode('latin-1')
    decrypted_blocks = []
    for i in range(0, len(encrypted_binary), 8):
        block = encrypted_binary[i:i+8]
        block_bin = string_to_binary(block)
        decrypted_block = des_decrypt_block(block_bin, subkeys)
        decrypted_blocks.append(binary_to_string(decrypted_block))
    decrypted_message = ''.join(decrypted_blocks)
    return decrypted_message.rstrip('\x00')

# ==================== CHAT ROOM ====================
active_clients = set()
recent_messages = []

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            action = data.get('action')
            
            if action == 'get_server_public_key':
                e, n = server_public_key
                response = {
                    'status': 'success',
                    'e': str(e),
                    'n': str(n)
                }
                
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
                recent_messages[:] = [msg for msg in recent_messages if msg.get('recipient') != client_name]
                print(f"[CLEAR] Old messages for {client_name} cleared")
                
                response = {'status': 'success', 'message': 'Key exchange completed'}
            
            elif action == 'send_message':
                encrypted_msg = data['message']
                client_name = data.get('client_name', 'Unknown')
                
                if client_name in client_des_keys:
                    try:
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
                        
                        response = {'status': 'sent', 'success': True}
                        
                    except Exception as e:
                        print(f"[ERROR] Decrypt failed for {client_name}: {e}")
                        response = {'status': 'error', 'message': 'Decryption failed'}
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode())
                        return
                else:
                    response = {'status': 'error', 'message': 'No DES key found'}
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Limit message history
                if len(recent_messages) > 100:
                    recent_messages[:] = recent_messages[-100:]
                
            elif action == 'get_messages':
                client_name = data.get('client_name', '')
                messages = [msg for msg in recent_messages 
                           if msg.get('recipient') == client_name and msg['sender'] != client_name]
                response = {'status': 'success', 'messages': messages}
                
            elif action == 'join':
                client_num = 1
                while client_num in active_clients:
                    client_num += 1
                active_clients.add(client_num)
                client_name = f"Client_{client_num}"
                print(f"[JOIN] {client_name}")
                response = {'status': 'joined', 'client_name': client_name}
                
            elif action == 'quit':
                client_name = data.get('client_name', '')
                if client_name.startswith('Client_'):
                    try:
                        client_num = int(client_name.split('_')[1])
                        active_clients.discard(client_num)
                        print(f"[QUIT] {client_name}")
                    except ValueError:
                        pass
                response = {'status': 'quit'}
                
            else:
                response = {'status': 'connected'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def log_message(self, format, *args):
        # Suppress default HTTP logging
        pass

def main():
    PORT = 65432
    
    print("="*60)
    print("SECURE CHAT SERVER (RSA + DES)")
    print("="*60)
    print(f"Port: {PORT}")
    e, n = server_public_key
    print(f"RSA Public Key (e): {e}")
    print(f"RSA Public Key (n): {str(n)[:50]}...")
    print("="*60)
    print("Server siap menerima koneksi...\n")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer dihentikan")
        sys.exit(0)

if __name__ == "__main__":
    main()