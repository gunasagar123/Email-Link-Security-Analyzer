import os
from datetime import timedelta

class Config:
    """
    Complete Configuration for Email & Link Security Analyzer
    Contains all settings for Flask app, security, file handling, and database
    """
    
    # ==================== FLASK CORE SETTINGS ====================
    
    # Secret key for session encryption and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production-2024'
    
    # Debug mode - Set to False in production
    DEBUG = False 
    
    # Testing mode
    TESTING = False
    
    # ==================== FILE UPLOAD SETTINGS ====================
    
    # Upload folder path - where temporary files are stored
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    
    # Maximum file size (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {
        # Text formats
        'txt', 'text', 'log',
        
        # Data formats
        'json', 'csv', 'tsv',
        
        # Email formats
        'eml', 'msg', 'emlx',
        
        # Document formats (for future expansion)
        'doc', 'docx', 'pdf', 'rtf',
        
        # Web formats
        'html', 'htm', 'xml'
    }
    
    # ==================== DATABASE SETTINGS ====================
    
    # SQLite database path
    DATABASE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'database', 
        'users.db'
    )
    
    # Database connection settings
    DATABASE_TIMEOUT = 30  # seconds
    DATABASE_CHECK_SAME_THREAD = False
    
    # ==================== SESSION SETTINGS ====================
    
    # Session cookie name
    SESSION_COOKIE_NAME = 'email_analyzer_session'
    
    # Session cookie settings
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Session lifetime (24 hours)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # ==================== SECURITY SETTINGS ====================
    
    # Password hashing algorithm
    PASSWORD_HASH_ALGORITHM = 'sha256'
    
    # Minimum password length
    MIN_PASSWORD_LENGTH = 6
    
    # Maximum password length
    MAX_PASSWORD_LENGTH = 128
    
    # Session token length (bytes)
    SESSION_TOKEN_LENGTH = 32
    
    # ==================== ANALYSIS SETTINGS ====================
    
    # Maximum items to analyze in one batch
    MAX_ITEMS_PER_ANALYSIS = 1000
    
    # Maximum email body length (characters)
    MAX_EMAIL_BODY_LENGTH = 50000
    
    # Maximum URL length
    MAX_URL_LENGTH = 2048
    
    # Analysis timeout (seconds)
    ANALYSIS_TIMEOUT = 300  # 5 minutes
    
    # ==================== APPLICATION INFO ====================
    
    # Application name
    APP_NAME = "Email & Link Security Analyzer"
    
    # Application version
    APP_VERSION = "1.0.0"
    
    # Application description
    APP_DESCRIPTION = "Advanced phishing and scam detection tool"
    
    # Developer info
    DEVELOPER_NAME = "Your Name"
    DEVELOPER_EMAIL = "your.email@example.com"
    
    # ==================== UI SETTINGS ====================
    
    # Results per page (for pagination - future feature)
    RESULTS_PER_PAGE = 20
    
    # Maximum history items to display
    MAX_HISTORY_ITEMS = 50
    
    # ==================== THREAT LEVEL COLORS ====================
    
    THREAT_COLORS = {
        'SAFE': '#10b981',      # Green
        'LOW': '#f59e0b',       # Yellow
        'MEDIUM': '#f97316',    # Orange
        'HIGH': '#ef4444',      # Red
        'CRITICAL': '#dc2626'   # Dark Red
    }
    
    # ==================== LOGGING SETTINGS ====================
    
    # Enable logging
    ENABLE_LOGGING = True
    
    # Log file path
    LOG_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'logs', 
        'app.log'
    )
    
    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL = 'INFO'
    
    # ==================== FEATURE FLAGS ====================
    
    # Enable user registration
    ENABLE_REGISTRATION = True
    
    # Enable analysis history
    ENABLE_HISTORY = True
    
    # Enable PDF export (future feature)
    ENABLE_PDF_EXPORT = False
    
    # Enable email notifications (future feature)
    ENABLE_EMAIL_NOTIFICATIONS = False
    
    # ==================== RATE LIMITING (Future Feature) ====================
    
    # Maximum analyses per user per hour
    MAX_ANALYSES_PER_HOUR = 100
    
    # Maximum file uploads per user per day
    MAX_UPLOADS_PER_DAY = 50
    
    # ==================== PARSER SETTINGS ====================
    
    # Maximum number of emails to extract from a single file
    MAX_EMAILS_PER_FILE = 500
    
    # Maximum number of links to extract from a single file
    MAX_LINKS_PER_FILE = 1000
    
    # Enable smart parsing fallback
    ENABLE_SMART_PARSING = True
    
    # ==================== INITIALIZATION ====================
    
    @staticmethod
    def init_app(app):
        """
        Initialize application with configuration
        Creates necessary directories and sets up environment
        """
        
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Create database folder if it doesn't exist
        os.makedirs(
            os.path.dirname(Config.DATABASE_PATH), 
            exist_ok=True
        )
        
        # Create logs folder if logging is enabled
        if Config.ENABLE_LOGGING:
            os.makedirs(
                os.path.dirname(Config.LOG_FILE), 
                exist_ok=True
            )
        
        # Set up logging
        if Config.ENABLE_LOGGING:
            import logging
            logging.basicConfig(
                filename=Config.LOG_FILE,
                level=getattr(logging, Config.LOG_LEVEL),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Print startup message
        if Config.DEBUG:
            print("=" * 60)
            print(f"🛡️  {Config.APP_NAME} v{Config.APP_VERSION}")
            print("=" * 60)
            print(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
            print(f"💾 Database: {Config.DATABASE_PATH}")
            print(f"🔒 Debug mode: {Config.DEBUG}")
            print(f"📊 Max items per analysis: {Config.MAX_ITEMS_PER_ANALYSIS}")
            print("=" * 60)


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Override with environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or Config.DATABASE_PATH


class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # In-memory database for testing
    MAX_ITEMS_PER_ANALYSIS = 10  # Smaller limit for testing


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    """Get configuration object by name"""
    return config.get(config_name, config['default'])