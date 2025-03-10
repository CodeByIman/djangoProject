from django.utils.deprecation import MiddlewareMixin

class JWTFromSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If there's an access token in session, add it to the Authorization header
        access_token = request.session.get('access_token')
        if access_token and 'HTTP_AUTHORIZATION' not in request.META:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        return None