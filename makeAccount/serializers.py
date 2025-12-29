from rest_framework import serializers
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # optional doctor fields
    specialty = serializers.CharField(required=False, allow_blank=True)
    fee = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'phone', 'category', 'password', 'specialty', 'fee']

    def create(self, validated_data):
        # Extract doctor fields but keep optional
        specialty = validated_data.pop('specialty', 'General')
        fee = validated_data.pop('fee', 'PKR 2000')

        user = User(
            username=validated_data['username'],
            phone=validated_data['phone'],
            category=validated_data['category'],
        )
        user.set_password(validated_data['password'])
        user.save()

        # You can optionally create Doctor here, or leave it to the view
        return user
