"""scraper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from djangospider import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.scrape_and_display),
    path('scrape_and_display/', views.scrape_and_display, name='scrape_and_display'),
    path('update_scrapy_status', views.update_scrapy_status, name='update_scrapy_status'),
    path('check_scrapy_status/<str:username>/', views.check_scrapy_status, name='check_scrapy_status'),
    path('cancel_scrapy_task/<str:username>/', views.cancel_scrapy_task, name='cancel_scrapy_task'),
]
