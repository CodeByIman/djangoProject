from django.urls import path
from api.views import ListingListView, ListingCreateView, ListingDetailView, ListingUpdateDeleteView,UserRegistrationView, LoginView

urlpatterns = [
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('listings/', ListingListView.as_view(), name='listings'),
    path('listings/create/', ListingCreateView.as_view(), name='create_listing'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing_detail'),
    path('listings/<int:pk>/edit/', ListingUpdateDeleteView.as_view(), name='edit_listing'),
]
