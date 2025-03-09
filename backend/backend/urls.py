from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from api.views import (
    ListingListView, 
    ListingCreateView, 
    ListingDetailView, 
    ListingUpdateDeleteView, 
    LoginView,
    register_page,
    UserRegistrationView,
    home,
    login_page,
    listing_view,
    LoginView,
    LogoutView,
    HomePageView,

)
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='api_register'),  # Unique name
    # path('login/', LoginView.as_view(), name='api_login'),  # Unique name
    path('listings/', ListingListView.as_view(), name='listings'),
    path('listings/create/', ListingCreateView.as_view(), name='create_listing'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing_detail'),
    path('listings/<int:pk>/edit/', ListingUpdateDeleteView.as_view(), name='edit_listing'),
    path('home/', home, name='home'),
    # path('register/', register_page, name='register'),  # Unique name
    # path('login/', login_page, name='login'),
      path('', listing_view, name='listing'),   # Template-based login
      path('login/', LoginView.as_view(), name='login'),
       path('home/', HomePageView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)