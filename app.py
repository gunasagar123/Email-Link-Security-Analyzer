from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from functools import wraps

# CRITICAL FIX: Ensure directories exist BEFORE imports
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('src', exist_ok=True)

from config import Config
from src.auth import AuthManager
from src.parsers import parse_uploaded_file
from src.analyzer import EmailLinkAnalyzer


app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize managers
auth_manager = AuthManager(app.config['DATABASE_PATH'])
analyzer = EmailLinkAnalyzer()


# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        user = auth_manager.verify_session(session['session_id'])
        if not user:
            session.clear()
            flash('Session expired. Please login again', 'warning')
            return redirect(url_for('login'))
        
        # Store user in request context for easy access
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def serialize_results(results):
    """Convert analysis results to JSON-serializable format"""
    return [
        {
            'content': r.content,
            'risk_score': r.risk_score,
            'threat_level': r.threat_level.label,
            'threat_emoji': r.threat_level.emoji,
            'flags': r.flags,
            'analysis_type': r.analysis_type,
            'is_suspicious': r.is_suspicious()
        }
        for r in results
    ]


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Landing page - redirect to login or dashboard"""
    if 'session_id' in session:
        user = auth_manager.verify_session(session['session_id'])
        if user:
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        result = auth_manager.login_user(username, password)
        
        if result['success']:
            session['session_id'] = result['session_id']
            session['user'] = result['user']
            session.permanent = True
            flash(f'Welcome back, {result["user"]["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result.get('message', 'Login failed'), 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('login.html', show_register=True)
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('login.html', show_register=True)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('login.html', show_register=True)
        
        result = auth_manager.register_user(username, email, password)
        
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result.get('message', 'Registration failed'), 'danger')
            return render_template('login.html', show_register=True)
    
    return render_template('login.html', show_register=True)


@app.route('/logout')
def logout():
    """Logout user"""
    if 'session_id' in session:
        auth_manager.logout_user(session['session_id'])
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))


# ==================== MAIN APPLICATION ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with analysis options"""
    user = request.current_user
    history = auth_manager.get_user_history(user['id'], limit=5)
    return render_template('dashboard.html', user=user, history=history)


@app.route('/upload/<analysis_type>')
@login_required
def upload_page(analysis_type):
    """Upload page for specific analysis type"""
    if analysis_type not in ['email', 'link', 'manual']:
        flash('Invalid analysis type', 'danger')
        return redirect(url_for('dashboard'))
    
    user = request.current_user
    return render_template('upload.html', 
                         analysis_type=analysis_type, 
                         user=user)


# ==================== FILE UPLOAD & ANALYSIS ROUTES ====================

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload and analysis"""
    try:
        user = request.current_user
        
        # Get analysis type
        analysis_type = request.form.get('type', '')
        
        if analysis_type not in ['email', 'link']:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{user['id']}_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # FIXED: Read file content with better encoding handling
        content = None
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"Successfully read file with {encoding} encoding")
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if content is None:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'Unable to read file. Please ensure it is a valid text file.'
            }), 400
        
        # Parse file using smart parser
        parsed_data = parse_uploaded_file(content, filename, analysis_type)
        
        if not parsed_data['success']:
            os.remove(filepath)  # Clean up
            return jsonify({
                'success': False,
                'error': 'Failed to parse file'
            }), 400
        
        # Analyze data
        results = []
        
        if analysis_type == 'email':
            for email_data in parsed_data['data']:
                result = analyzer.analyze_email(email_data)
                results.append(result)
        
        elif analysis_type == 'link':
            for link in parsed_data['data']:
                result = analyzer.analyze_link(link)
                results.append(result)
        
        # Store results in session
        serialized_results = serialize_results(results)
        session['analysis_results'] = serialized_results
        session['analysis_type'] = analysis_type
        session['analysis_timestamp'] = datetime.now().isoformat()
        
        # Calculate statistics
        total = len(results)
        suspicious = sum(1 for r in results if r.is_suspicious())
        safe = total - suspicious
        avg_score = sum(r.risk_score for r in results) / total if total > 0 else 0
        
        # Save to history
        auth_manager.save_analysis_history(user['id'], {
            'type': analysis_type,
            'total': total,
            'suspicious': suspicious,
            'safe': safe,
            'avg_score': avg_score
        })
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'redirect': url_for('results'),
            'stats': {
                'total': total,
                'suspicious': suspicious,
                'safe': safe
            }
        })
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500


@app.route('/api/analyze-manual', methods=['POST'])
@login_required
def analyze_manual():
    """Handle manual entry analysis"""
    try:
        user = request.current_user
        data = request.get_json()
        
        analysis_type = data.get('type', '')
        
        if analysis_type == 'email':
            email_data = {
                'sender': data.get('sender', ''),
                'subject': data.get('subject', ''),
                'body': data.get('body', ''),
                'links': data.get('links', [])
            }
            result = analyzer.analyze_email(email_data)
        
        elif analysis_type == 'link':
            url = data.get('url', '')
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            result = analyzer.analyze_link(url)
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type'
            }), 400
        
        # Store single result
        serialized_results = serialize_results([result])
        session['analysis_results'] = serialized_results
        session['analysis_type'] = analysis_type
        session['analysis_timestamp'] = datetime.now().isoformat()
        
        # Save to history
        auth_manager.save_analysis_history(user['id'], {
            'type': f'{analysis_type}_manual',
            'total': 1,
            'suspicious': 1 if result.is_suspicious() else 0,
            'safe': 0 if result.is_suspicious() else 1,
            'avg_score': result.risk_score
        })
        
        return jsonify({
            'success': True,
            'redirect': url_for('results')
        })
    
    except Exception as e:
        print(f"Manual analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500


# ==================== RESULTS ROUTE ====================

@app.route('/results')
@login_required
def results():
    """Display analysis results"""
    user = request.current_user
    
    # Get results from session
    analysis_results = session.get('analysis_results', [])
    analysis_type = session.get('analysis_type', '')
    analysis_timestamp = session.get('analysis_timestamp', '')
    
    if not analysis_results:
        flash('No analysis results found. Please perform an analysis first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Calculate statistics
    total = len(analysis_results)
    suspicious = sum(1 for r in analysis_results if r['is_suspicious'])
    safe = total - suspicious
    avg_score = sum(r['risk_score'] for r in analysis_results) / total if total > 0 else 0
    
    # Separate suspicious and safe items
    suspicious_results = [r for r in analysis_results if r['is_suspicious']]
    safe_results = [r for r in analysis_results if not r['is_suspicious']]
    
    # Sort by risk score (highest first)
    suspicious_results.sort(key=lambda x: x['risk_score'], reverse=True)
    
    statistics = {
        'total': total,
        'suspicious': suspicious,
        'safe': safe,
        'avg_score': round(avg_score, 1),
        'timestamp': analysis_timestamp
    }
    
    return render_template('results.html',
                         user=user,
                         statistics=statistics,
                         suspicious_results=suspicious_results,
                         safe_results=safe_results,
                         analysis_type=analysis_type)


@app.route('/history')
@login_required
def history():
    """View analysis history"""
    user = request.current_user
    history_data = auth_manager.get_user_history(user['id'], limit=20)
    return render_template('history.html', user=user, history=history_data)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    flash('Page not found', 'warning')
    return redirect(url_for('dashboard'))


@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.', 'danger')
    return redirect(url_for('dashboard'))


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum size is 16MB.', 'danger')
    return redirect(url_for('dashboard'))


# ==================== UTILITY ROUTES ====================

@app.route('/clear-session')
@login_required
def clear_session():
    """Clear analysis results from session"""
    session.pop('analysis_results', None)
    session.pop('analysis_type', None)
    session.pop('analysis_timestamp', None)
    flash('Session cleared', 'info')
    return redirect(url_for('dashboard'))


# ==================== MAIN ====================

if __name__ == '__main__':
    # Ensure all directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)
    
    # Cleanup expired sessions on startup
    try:
        auth_manager.cleanup_expired_sessions()
    except Exception as e:
        print(f"Warning: Could not cleanup sessions: {e}")
    
    print("\n" + "="*70)
    print("EMAIL & LINK SECURITY ANALYZER")
    print("="*70)
    print("Server starting...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Database: {app.config['DATABASE_PATH']}")
    print("="*70)
    print("\nOPEN YOUR BROWSER:")
    print("   http://localhost:5000")
    print("\nDEMO LOGIN:")
    print("   Username: demo")
    print("   Password: demo123")
    print("\nPress CTRL+C to stop the server")
    print("="*70 + "\n")
    
    try:
        # Run application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()