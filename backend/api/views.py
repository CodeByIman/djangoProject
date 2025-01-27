from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Listing, University
from .serializers import (
    ListingSerializer,
    ListingCreateSerializer,
    UniversitySerializer,
    UserSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.parsers import JSONParser
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()  # Reference the custom User model


class UserRegistrationView(APIView):
    permission_classes = []  # No authentication needed for registration

    def post(self, request):
        # Get the data from the request body
        data = request.data
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return Response(
                {"error": "Username, password, and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Public access for login

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            # Issue JWT Token
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


# List and filter listings
class ListingListView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        queryset = Listing.objects.all()
        university_name = self.request.query_params.get("university", None)
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        property_type = self.request.query_params.get("type", None)

        if university_name:
            queryset = queryset.filter(university__name__icontains=university_name)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if property_type:
            queryset = queryset.filter(property_type=property_type)

        return queryset


# Add a listing (for sellers only)
class ListingCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not getattr(request.user, "is_seller", False):  # Check seller attribute
            return Response(
                {"error": "Only sellers can create listings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ListingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Listing details
class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


# Update/Delete a listing (seller only)
class ListingUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk, seller=request.user)
        except Listing.DoesNotExist:
            return Response(
                {"error": "Listing not found or you don't have permission to edit it"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ListingCreateSerializer(listing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk, seller=request.user)
            listing.delete()
            return Response(
                {"message": "Listing deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Listing.DoesNotExist:
            return Response(
                {"error": "Listing not found or you don't have permission to delete it"},
                status=status.HTTP_404_NOT_FOUND,
            )
