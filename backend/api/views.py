from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404 ,redirect
from .models import Listing, University
from .serializers import (
    ListingSerializer,
    ListingCreateSerializer,
    UniversitySerializer,
    UserSerializer,
)

User = get_user_model()  # Référence au modèle d'utilisateur personnalisé


# ✅ User Registration View
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]  # Accessible sans authentification

    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return Response(
                {"error": "Username, password, and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED,
        )
 
def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            return render(request, "register.html", {"error": "All fields are required."})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists."})

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "register.html", {"error": str(e)})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        print("User registered successfully! Redirecting to login page...")  # Debug statement
        return redirect('login_page')  # Ensure this matches the URL name in urls.py

    return render(request, "register.html")
# # ✅ Login View (JWT Token)
# class LoginView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         user = authenticate(username=username, password=password)
#         if user:
#             refresh = RefreshToken.for_user(user)
#             return Response(
#                 {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username") if request.content_type == 'application/json' else request.POST.get("username")
        password = request.data.get("password") if request.content_type == 'application/json' else request.POST.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            error_message = {"error": "Invalid credentials"}
            return Response(error_message, status=status.HTTP_401_UNAUTHORIZED) if request.content_type == 'application/json' else render(request, 'api/login.html', error_message)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        if request.content_type == 'application/json':
            return Response({"refresh": str(refresh), "access": access_token}, status=status.HTTP_200_OK)
        else:
            request.session['access_token'] = access_token
            return redirect('/')  # Redirect to home page

def login_page(request):
    return render(request, 'login.html')

# # ✅ List and filter listings
# class ListingListView(generics.ListAPIView):
#     serializer_class = ListingSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         queryset = Listing.objects.all()
#         university_name = self.request.query_params.get("university", None)
#         min_price = self.request.query_params.get("min_price", None)
#         max_price = self.request.query_params.get("max_price", None)
#         property_type = self.request.query_params.get("type", None)

#         if university_name:
#             queryset = queryset.filter(university__name__icontains=university_name)
#         if min_price:
#             queryset = queryset.filter(price__gte=min_price)
#         if max_price:
#             queryset = queryset.filter(price__lte=max_price)
#         if property_type:
#             queryset = queryset.filter(property_type=property_type)

#         return queryset
class ListingListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Listing.objects.all()
        university_name = self.request.query_params.get("university", None)
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        property_type = self.request.query_params.get("type", None)

        if university_name:
            queryset = queryset.filter(university__icontains=university_name)  # Filter directly on the university CharField
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if property_type:
            queryset = queryset.filter(property_type=property_type)

        return queryset











def listing_view(request):
    return render(request, "listing.html") 
    
# ✅ Add a listing (for authenticated users)
class ListingCreateView(generics.CreateAPIView):
    serializer_class = ListingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# ✅ Listing details
class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]


# ✅ Update/Delete a listing (only for the seller)
class ListingUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk, seller=request.user)
        serializer = ListingCreateSerializer(listing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk, seller=request.user)
        listing.delete()
        return Response(
            {"message": "Listing deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )



def listing_view(request):
    listings = Listing.objects.all()
    return render(request, "listing.html", {"listings": listings})

def home(request):
    return render(request, 'home.html', {'message': 'Template is working!'})
