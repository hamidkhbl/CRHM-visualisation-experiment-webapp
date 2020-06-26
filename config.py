class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "tZ1KIEOX5muYllhOCheKyg"
    DB_NAME = "site.db"
    DB_USERNAME = "root"
    DB_PASSWORD = "test"
    FILE_UPLOADS = "E:/Google Drive/git/flask-app-sample/data"
    ALLOWED_FILE_EXTENTIONS = ["OBS"]
    MAX_FILE_SIZE = 0.5 * 1024 * 1024
    OBS_FILES_DIR = "E:/Google Drive/git/CRHM_Visualisation/data/obs_files"
    CRHM_APP_DIR = "E:/Google Drive/git/CRHM_Visualisation/data/crhm_app"
    FILE_UPLOADS = "E:/Google Drive/git/CRHM_Visualisation/data/users_data"


    UPLOADS = "/"

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    ENV = 'production'
    pass

class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    SESSION_COOKIE_SECURE = False
