from rest_framework import serializers
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("Ce compte est désactivé.")
                return user
            else:
                raise serializers.ValidationError("Nom d’utilisateur ou mot de passe incorrect.")
        else:
            raise serializers.ValidationError("Les deux champs sont requis.")


