from django.contrib.auth.models import AbstractUser
from django.db import models

# Utilisateur personnalisé
class User(AbstractUser):
    is_seller = models.BooleanField(default=False)  # Indique si un utilisateur est un vendeur

# Universités
class University(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Modèle pour les annonces
class Listing(models.Model):
    PROPERTY_TYPES = [
        ('room', 'Chambre'),
        ('studio', 'Studio'),
        ('apartment', 'Appartement'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(choices=PROPERTY_TYPES, max_length=20)
    location = models.CharField(max_length=255)
    university = models.CharField(max_length=255, null=True, blank=True)  # Now just a simple field
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(default=0.0)  # Default value for latitude
    longitude = models.FloatField(default=0.0)
    images = models.ImageField(upload_to='listing_images/', null=True, blank=True)

    def __str__(self):
        return self.title
