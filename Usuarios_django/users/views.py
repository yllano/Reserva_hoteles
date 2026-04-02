from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginValidateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # In Django, authenticate usually takes username. If we use email:
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
            if user:
                return Response({'status': 'OK', 'user': UserSerializer(user).data})
        except User.DoesNotExist:
            pass
            
        return Response({'status': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Dado un correo, devuelve la pregunta de seguridad del usuario."""
        email = request.data.get('email')
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            return Response({
                'email': email,
                'security_question': profile.security_question
            })
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Este usuario no tiene pregunta de seguridad configurada.'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Verifica la respuesta de seguridad y actualiza la contraseña."""
        email = request.data.get('email')
        security_answer = request.data.get('security_answer', '').lower().strip()
        new_password = request.data.get('new_password')

        if not email or not security_answer or not new_password:
            return Response({'error': 'Email, respuesta de seguridad y nueva contraseña son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            if profile.security_answer != security_answer:
                return Response({'error': 'La respuesta de seguridad es incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Contraseña actualizada correctamente.'})
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Este usuario no tiene pregunta de seguridad configurada.'}, status=status.HTTP_400_BAD_REQUEST)
