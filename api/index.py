from http.server import BaseHTTPRequestHandler
import json
import hashlib
import time
import random
import string
from datetime import datetime

# In-memory storage (Vercel serverless restart पर data reset होगा)
USERS = {}
SESSIONS = {}

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

class handler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        parsed_path = self.path.split('?')
        path = parsed_path[0]
        query = {}
        if len(parsed_path) > 1:
            for param in parsed_path[1].split('&'):
                if '=' in param:
                    key, val = param.split('=', 1)
                    query[key] = val
        
        # ATTACK endpoint
        if path == '/attack':
            token = query.get('token', '')
            target = query.get('target', '')
            
            if not token or token not in SESSIONS:
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Invalid token'}).encode())
                return
            
            if not target:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Target URL required'}).encode())
                return
            
            self._set_headers(200)
            self.wfile.write(json.dumps({
                'status': 'attack_started',
                'message': '⚠️ EDUCATIONAL PURPOSE ONLY ⚠️',
                'target': target,
                'time': datetime.now().isoformat(),
                'created_by': 'SATVIR'
            }).encode())
            return
        
        # STATUS endpoint
        if path == '/status':
            token = query.get('token', '')
            if token in SESSIONS:
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    'status': 'active',
                    'username': SESSIONS[token]['username']
                }).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Invalid token'}).encode())
            return
        
        # Home endpoint
        self._set_headers(200)
        self.wfile.write(json.dumps({
            'status': 'online',
            'message': 'API is working!',
            'endpoints': ['/register (POST)', '/login (POST)', '/attack (GET)', '/status (GET)'],
            'created_by': 'SATVIR'
        }).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        # REGISTER endpoint
        if self.path == '/register':
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            if not username or not password:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Username and password required'}).encode())
                return
            
            if username in USERS:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Username exists'}).encode())
                return
            
            USERS[username] = {
                'password': hash_password(password),
                'created': datetime.now().isoformat()
            }
            self._set_headers(200)
            self.wfile.write(json.dumps({'status': 'success', 'message': 'Registered', 'username': username}).encode())
            return
        
        # LOGIN endpoint
        if self.path == '/login':
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            if username not in USERS or USERS[username]['password'] != hash_password(password):
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
                return
            
            token = generate_token()
            SESSIONS[token] = {'username': username, 'expires': time.time() + 86400}
            self._set_headers(200)
            self.wfile.write(json.dumps({'status': 'success', 'token': token, 'username': username}).encode())
            return
        
        # 404 for other POST paths
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())
