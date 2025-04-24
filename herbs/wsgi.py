"""
WSGI config for herbs project.
"""

import os
from django.core.wsgi import get_wsgi_application  # 导入Django的WSGI应用程序

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbs.settings')  # 设置Django的设置模块

application = get_wsgi_application()  # 获取WSGI应用程序实例