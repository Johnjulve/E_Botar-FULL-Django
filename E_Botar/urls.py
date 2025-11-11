"""
URL configuration for E_Botar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from voting_module.views import home_view, voting_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('auth_module.urls')),
    path('candidates/', include('candidate_module.urls')),
    path('elections/', include('election_module.urls')),
    path('voting/', include('voting_module.urls')),
    path('votes/', include(('voting_module.urls', 'votes'), namespace='votes')),
    path('admin-ui/', include('admin_module.urls')),
    # Back-compat: keep old prefix but point to same admin urls
    path('custom-admin/', include(('admin_module.urls', 'admin_module'), namespace='admin_legacy')),
    path('security/', include('security_module.urls')),
    path('results/', include('result_module.urls')),
    path('login/', lambda request: redirect('/auth/login/')),
    path('administration/', lambda request: redirect('/admin-ui/')),
    path('', home_view, name='home'),
    path('history/', voting_history, name='voting_history'),
]

# Add media files support for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
