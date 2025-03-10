from rest_framework.views import APIView
from django.views import View
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model,login
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
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

User = get_user_model()  # Référence au modèle d'utilisateur personnalisé

# Setup logger
logger = logging.getLogger(__name__)

# ✅ User Registration View with CSRF handling and enhanced error logging
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]  # Accessible sans authentification
    
    def get(self, request):
        # Render the registration template for GET requests
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        # Validation
        if not username or not password or not email:
            logger.error("Validation failed: Username, password, and email are required.")
            return render(request, 'register.html', {"error": "Username, password, and email are required."})

        if User.objects.filter(username=username).exists():
            logger.warning(f"Username '{username}' already exists.")
            return render(request, 'register.html', {"error": "Username already exists."})

        try:
            validate_password(password)
        except ValidationError as e:
            logger.error(f"Password validation failed: {str(e)}")
            return render(request, 'register.html', {"error": str(e)})

        # Create the new user
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            logger.info(f"User '{username}' registered successfully.")
        except Exception as e:
            logger.error(f"Error creating user '{username}': {str(e)}")
            return render(request, 'register.html', {"error": "An error occurred while creating the user. Please try again."})

        # If successful, render success message or redirect to login
        return redirect('/login')  # Redirect to login page after successful registration
# # ✅ User Registration View
# class UserRegistrationView(APIView):
#     permission_classes = [permissions.AllowAny]  # Accessible sans authentification

#     def post(self, request):
#         data = request.data
#         username = data.get("username")
#         password = data.get("password")
#         email = data.get("email")

#         if not username or not password or not email:
#             return Response(
#                 {"error": "Username, password, and email are required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if User.objects.filter(username=username).exists():
#             return Response(
#                 {"error": "Username already exists."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             validate_password(password)
#         except ValidationError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         user = User.objects.create_user(username=username, password=password, email=email)
#         user.save()

#         return Response(
#             {"message": "User registered successfully!"},
#             status=status.HTTP_201_CREATED,
#         )
 
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
    
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        # Try to get username/password from POST data (form submission)
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            # Return the template with error message
            return render(request, 'login.html', {'error': 'Invalid credentials, please try again.'})
        
        # Log the user in (this sets the session)
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Store the token in session
        request.session['access_token'] = access_token
        
        # Store user information in session
        request.session['user_info'] = {
            'username': user.username,
            'email': user.email,
            'id': user.id,
        }
        
        # Save the session explicitly
        request.session.save()
        
        # Return JSON response for axios or redirect for form submit
        if request.content_type == 'application/json' or 'multipart/form-data' in request.content_type:
            return JsonResponse({
                'success': True,
                'redirect': '/home/'
            })
        else:
            return redirect('/home/')
    
# class LoginView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         username = request.data.get("username") if request.content_type == 'application/json' else request.POST.get("username")
#         password = request.data.get("password") if request.content_type == 'application/json' else request.POST.get("password")

#         user = authenticate(username=username, password=password)
#         if not user:
#             error_message = {"error": "Invalid credentials"}
#             return Response(error_message, status=status.HTTP_401_UNAUTHORIZED) if request.content_type == 'application/json' else render(request, 'api/login.html', error_message)

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)

#         if request.content_type == 'application/json':
#             return Response({"refresh": str(refresh), "access": access_token}, status=status.HTTP_200_OK)
#         else:
#             request.session['access_token'] = access_token
#             return redirect('/')  # Redirect to home page

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

class LogoutView(APIView):
    def get(self, request):
        # Clear the session
        request.session.flush()
        
        # Redirect to login page
        return redirect('/login')
    

from rest_framework.views import APIView
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)

class HomePageView(APIView):
    def get(self, request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            logger.warning("User not authenticated, redirecting to login")
            return redirect('/login')
            
        # Get user info from session or user object
        user_info = request.session.get('user_info')
        
        # If session doesn't have user_info, create it from user object
        if not user_info:
            logger.info("Recreating user_info in session")
            user_info = {
                'username': request.user.username,
                'email': request.user.email,
                'id': request.user.id,
            }
            request.session['user_info'] = user_info
            request.session.save()
        
        # Debug logging
        logger.debug(f"Access Token: {request.session.get('access_token')}")
        logger.debug(f"User Info: {user_info}")
            
        # Render home page with user info
        return render(request, 'home.html', {'user': user_info})    



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



class ListingCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # The middleware will handle setting the JWT token from session
        
        if not request.user.is_authenticated:
            return redirect('/login')

        user_info = request.session.get('user_info', {
            'username': request.user.username,
            'email': request.user.email,
            'id': request.user.id,
        })
        
        return render(request, 'create.html', {'user': user_info})
        
    def post(self, request):
        # Handle your create listing logic here
        serializer = ListingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return redirect('/home')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth(request):
    return Response({'authenticated': True})



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
