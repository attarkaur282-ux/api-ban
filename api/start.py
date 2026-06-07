import json
import hashlib
import time
import random
import string
from datetime import datetime

USERS = {}
SESSIONS = {}

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def handler(request, context):
    method = request.method or 'GET'
    path = request.path or '/'
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    query = request.query or {}
    body = {}
    if request.body:
        try:
            body = json.loads(request.body)
        except:
            pass
    
    # REGISTER
    if path == '/register' and method == 'POST':
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        if not username or not password:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Username and password required'})}
        if username in USERS:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Username exists'})}
        USERS[username] = {'password': hash_password(password), 'created': datetime.now().isoformat()}
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'success', 'message': 'Registered', 'username': username})}
    
    # LOGIN
    if path == '/login' and method == 'POST':
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        if username not in USERS or USERS[username]['password'] != hash_password(password):
            return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'error': 'Invalid credentials'})}
        token = generate_token()
        SESSIONS[token] = {'username': username, 'expires': time.time() + 86400}
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'success', 'token': token, 'username': username})}
    
    # ATTACK
    if path == '/attack' and method == 'GET':
        token = query.get('token', '')
        target = query.get('target', '')
        if not token or token not in SESSIONS:
            return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'error': 'Invalid token'})}
        if not target:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Target URL required'})}
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'attack_started', 'message': 'EDUCATIONAL PURPOSE ONLY', 'target': target, 'time': datetime.now().isoformat(), 'created_by': 'SATVIR'})}
    
    # STATUS
    if path == '/status' and method == 'GET':
        token = query.get('token', '')
        if token in SESSIONS:
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'active', 'username': SESSIONS[token]['username']})}
        return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'error': 'Invalid token'})}
    
    # HOME
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'online', 'message': 'API is working', 'endpoints': ['/register', '/login', '/attack', '/status'], 'created_by': 'SATVIR'})}
