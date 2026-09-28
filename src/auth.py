import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db_path: str = 'database/users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,
                item_count INTEGER,
                suspicious_count INTEGER,
                safe_count INTEGER,
                average_score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default demo user if no users exist
        self.create_demo_user()
    
    def create_demo_user(self):
        """Create a demo user for testing"""
        try:
            self.register_user('demo', 'demo@example.com', 'demo123')
        except:
            pass  # User already exists
    
    def hash_password(self, password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user
        Returns: {'success': bool, 'message': str, 'user_id': int}
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                         (username, email))
            if cursor.fetchone():
                conn.close()
                return {
                    'success': False,
                    'message': 'Username or email already exists'
                }
            
            # Insert new user
            password_hash = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user_id': user_id
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and create session
        Returns: {'success': bool, 'session_id': str, 'user': dict}
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify credentials
            password_hash = self.hash_password(password)
            cursor.execute(
                'SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?',
                (username, password_hash)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
            
            user_id, username, email = user
            
            # Update last login
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now(), user_id)
            )
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            cursor.execute(
                'INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
                (session_id, user_id, expires_at)
            )
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'session_id': session_id,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify if session is valid and not expired
        Returns user data if valid, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.email, s.expires_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            user_id, username, email, expires_at = result
            expires_at = datetime.fromisoformat(expires_at)
            
            # Check if session expired
            if datetime.now() > expires_at:
                self.logout_user(session_id)
                return None
            
            return {
                'id': user_id,
                'username': username,
                'email': email
            }
        
        except Exception:
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """Delete session (logout)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def save_analysis_history(self, user_id: int, analysis_data: Dict[str, Any]) -> bool:
        """Save analysis to user history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_history 
                (user_id, analysis_type, item_count, suspicious_count, safe_count, average_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                analysis_data.get('type', ''),
                analysis_data.get('total', 0),
                analysis_data.get('suspicious', 0),
                analysis_data.get('safe', 0),
                analysis_data.get('avg_score', 0.0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_history(self, user_id: int, limit: int = 10) -> list:
        """Get user's analysis history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT analysis_type, item_count, suspicious_count, 
                       safe_count, average_score, timestamp
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'type': row[0],
                    'items': row[1],
                    'suspicious': row[2],
                    'safe': row[3],
                    'avg_score': row[4],
                    'timestamp': row[5]
                }
                for row in history
            ]
        except Exception:
            return []
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))
            conn.commit()
            conn.close()
        except Exception:
            pass