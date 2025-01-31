from rest_framework import serializers
from .models import User, Listing, University

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'is_seller']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'city']

class ListingSerializer(serializers.ModelSerializer):
    images = serializers.ImageField(use_url=True) 
    seller = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'property_type', 'location', 'university', 'seller', 'created_at', 'updated_at', 'images']

class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'property_type', 'location', 'university', 'images']
