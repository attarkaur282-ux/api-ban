import json
import hashlib
import time
import random
import string
from datetime import datetime
from http.cookies import SimpleCookie

# Simple in-memory storage (for Vercel, use external DB for real persistence)
USERS_FILE = 'pass.json'
SESSIONS = {}

def load_users():
    try:
        with open('pass.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open('pass.json', 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def handler(request):
    method = request.method
    path = request.path
    query = request.query
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    # ========== REGISTER ==========
    if path == '/register' and method == 'POST':
        try:
            body = json.loads(request.body or '{}')
            username = body.get('username', '').strip()
            password = body.get('password', '').strip()
            
            if not username or not password:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Username and password required'})
                }
            
            users = load_users()
            if username in users:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Username already exists'})
                }
            
            users[username] = {
                'password': hash_password(password),
                'created_at': datetime.now().isoformat(),
                'api_calls': 0
            }
            save_users(users)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Registration successful',
                    'username': username
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': str(e)})
            }
    
    # ========== LOGIN ==========
    if path == '/login' and method == 'POST':
        try:
            body = json.loads(request.body or '{}')
            username = body.get('username', '').strip()
            password = body.get('password', '').strip()
            
            users = load_users()
            if username not in users:
                return {
                    'statusCode': 401,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid credentials'})
                }
            
            if users[username]['password'] != hash_password(password):
                return {
                    'statusCode': 401,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid credentials'})
                }
            
            token = generate_token()
            SESSIONS[token] = {'username': username, 'expires': time.time() + 86400}
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Login successful',
                    'token': token,
                    'username': username
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': str(e)})
            }
    
    # ========== ATTACK API (Protected) ==========
    if path == '/attack' and method == 'GET':
        token = query.get('token', '')
        target = query.get('target', '')
        
        if not token or token not in SESSIONS:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid or expired token'})
            }
        
        if not target:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Target URL required'})
            }
        
        # Update user stats
        session = SESSIONS[token]
        username = session['username']
        users = load_users()
        if username in users:
            users[username]['api_calls'] = users[username].get('api_calls', 0) + 1
            save_users(users)
        
        # Return attack response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'attack_started',
                'message': '⚠️ EDUCATIONAL PURPOSE ONLY ⚠️',
                'target': target,
                'username': username,
                'time': datetime.now().isoformat(),
                'attack_id': generate_token()[:16],
                'note': 'This is a simulated attack response',
                'created_by': 'SATVIR'
            }, indent=2)
        }
    
    # ========== STATUS API ==========
    if path == '/status' and method == 'GET':
        token = query.get('token', '')
        if token in SESSIONS:
            username = SESSIONS[token]['username']
            users = load_users()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'active',
                    'username': username,
                    'api_calls': users.get(username, {}).get('api_calls', 0),
                    'message': 'You are logged in'
                })
            }
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid token'})
        }
    
    # ========== DEFAULT ==========
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Not found'})
    }
