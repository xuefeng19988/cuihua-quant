"""
Phase 30: User Authentication System
Simple user authentication with session management.
"""

import os
import sys
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class UserAuth:
    """
    Simple user authentication system.
    """
    
    def __init__(self, users_file: str = None):
        if users_file is None:
            users_file = os.path.join(project_root, 'data', 'users.json')
        self.users_file = users_file
        self.sessions: Dict[str, Dict] = {}
        self.users = self._load_users()
        
    def _load_users(self) -> Dict:
        """Load users from file."""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_users(self):
        """Save users to file."""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
            
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return hashed, salt
        
    def register(self, username: str, password: str, role: str = 'user') -> Dict:
        """
        Register a new user.
        
        Returns:
            Dict with status and message
        """
        if username in self.users:
            return {'status': 'error', 'message': '用户名已存在'}
            
        hashed, salt = self._hash_password(password)
        self.users[username] = {
            'username': username,
            'password_hash': hashed,
            'salt': salt,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        self._save_users()
        
        return {'status': 'success', 'message': '注册成功'}
        
    def login(self, username: str, password: str) -> Dict:
        """
        Login user.
        
        Returns:
            Dict with status and session token
        """
        if username not in self.users:
            return {'status': 'error', 'message': '用户名或密码错误'}
            
        user = self.users[username]
        hashed, _ = self._hash_password(password, user['salt'])
        
        if hashed != user['password_hash']:
            return {'status': 'error', 'message': '用户名或密码错误'}
            
        # Create session
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            'username': username,
            'role': user['role'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        return {
            'status': 'success',
            'token': token,
            'username': username,
            'role': user['role']
        }
        
    def logout(self, token: str) -> bool:
        """Logout user by invalidating session."""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
        
    def verify_session(self, token: str) -> Optional[Dict]:
        """Verify session token."""
        if token not in self.sessions:
            return None
            
        session = self.sessions[token]
        expires = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires:
            del self.sessions[token]
            return None
            
        return session
        
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict:
        """Change user password."""
        if username not in self.users:
            return {'status': 'error', 'message': '用户不存在'}
            
        user = self.users[username]
        hashed, _ = self._hash_password(old_password, user['salt'])
        
        if hashed != user['password_hash']:
            return {'status': 'error', 'message': '旧密码错误'}
            
        new_hashed, new_salt = self._hash_password(new_password)
        self.users[username]['password_hash'] = new_hashed
        self.users[username]['salt'] = new_salt
        self._save_users()
        
        return {'status': 'success', 'message': '密码修改成功'}
        
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user info (without password)."""
        if username not in self.users:
            return None
            
        user = self.users[username].copy()
        del user['password_hash']
        del user['salt']
        return user
        
    def list_users(self) -> list:
        """List all users (without passwords)."""
        users = []
        for username, user in self.users.items():
            info = user.copy()
            del info['password_hash']
            del info['salt']
            users.append(info)
        return users


# Global auth instance
auth = UserAuth()
