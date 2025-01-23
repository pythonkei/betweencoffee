from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'coffee'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('coffee.urls')),
    path('cart/', include('cart.urls', namespace="cart")),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', auth_views.LoginView.as_view(template_name='registration/register.html'), name='register'),
]

# sources css, image file root
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
