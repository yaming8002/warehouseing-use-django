"""
Django settings for warehousing_server project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


os_environ = os.environ

# ALLOWED_HOSTS_VALUE = [
#     origin.strip() for origin in os_environ["MY_ALLOWED_HOSTS"].split(",") if origin
# ]
# print(f"ALLOWED_HOSTS_VALUE{ALLOWED_HOSTS_VALUE}")

# CSRF_TRUSTED_ORIGINS_VALUE = [
#     origin.strip()
#     for origin in os_environ["MY_CSRF_TRUSTED_ORIGINS"].split(",")
#     if origin
# ]
# print(f"CSRF_TRUSTED_ORIGINS_VALUE{CSRF_TRUSTED_ORIGINS_VALUE}")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "Dv*4JqwxMSClY$x2lVzy!yAeBkX5ZVF0*qbGnCYZI@T#T4CIxA@p&GgeiRhrLhC4"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ALLOWED_HOSTS_VALUE
# CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS_VALUE  # 使用環境變數的值
# Application definition

INSTALLED_APPS = [
    "import_export",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wcommon",
    "stock",
    "trans",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wcommon.middleware.LoginRequiredMiddleware",
    "wcommon.middleware.AuthenticationMiddleware",
    "wcommon.middleware.LoggingMiddleware",
]

ROOT_URLCONF = "warehousing_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

WSGI_APPLICATION = "warehousing_server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# db_user = os_environ["MYSQL_USERNAME"]
# db_pass = os_environ["MYSQL_PASSWORD"]
# db_host = os_environ["MYSQL_HOST"]
# db_port = os_environ["MYSQL_PORT"]
# 检查配置文件是否存在
config_file_path = f"{BASE_DIR}/config_json.json"
if os.path.exists(config_file_path):
    # 读取配置文件
    with open(config_file_path) as f:
        config_data = json.load(f)

    # 替换数据库配置
    if "database" in config_data:
        db_config = config_data["database"]
        db_user = db_config["USER"]
        db_pass = db_config["PASSWORD"]
        db_host = db_config["HOST"]
        db_port = db_config["PORT"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "warehousingdb",  # DB名稱
        "USER": db_user,  # 使用者帳號
        "PASSWORD": db_pass,  # 使用者密碼 os_environ['MY_DB_PASSWORD']
        "HOST": db_host,
        "PORT": db_port,
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "your_session_cookie_name"  # 自定义会话 cookie 名称
SESSION_SAVE_EVERY_REQUEST = True  # 在每个请求上都保存会话
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器后会话过期
SESSION_COOKIE_AGE = 1800  # 会话过期时间，单位秒（这里设置为30分钟）

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "wcommon.Muser"  # 'myapp' 是您的應用程序的名稱
LOGOUT_REDIRECT_URL = "/login/"  # 轉跳到登入畫面
LOGIN_URL = "/login/"  # 轉跳到登入畫面
APPEND_SLASH = False


# 配置日志记录器，可以设置为适当的级别（例如'INFO'、'DEBUG'）
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "{asctime} {levelname} [In function: {funcName}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },        
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './debug.log',
            "formatter": "detailed",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}
