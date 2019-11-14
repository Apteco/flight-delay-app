"""api_apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from example_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login_local/', views.login_local, name='login_local'),
    path('login_local/login_local_proc', views.login_local_proc, name='login_local_proc'),
    path('accounts/login/', views.not_logged_in, name='not_logged_in'),
    path('logout/', views.logout, name='logout'),
    path('logout_api/', views.logout_api, name='logout_api'),
    path('home/', views.home, name='home'),
    path('login_api/', views.login_api, name='login_api'),
    path('login_api/login_api_proc', views.login_api_proc, name='login_api_proc'),
    path('example_one/', views.example_one, name='example_one'),
    path('example_one/show_count', views.example_one_count, name='example_one_count'),
    path('example_two/', views.example_two, name='example_two'),
    path('example_two/show_graph', views.example_two_graph, name='example_two_graph'),
    path('example_three', views.example_three, name='example_three'),
    path('example_three/show_map', views.example_three_map, name='example_three_map'),
    path('example_four/', views.example_four, name='example_four'),
    path('example_four/show_map', views.example_four_map, name='example_four_map'),
]
