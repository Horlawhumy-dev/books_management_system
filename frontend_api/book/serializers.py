from rest_framework import serializers
from .models import Book, User

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name']


class BorrowerSerializer(serializers.Serializer):
    user_email = serializers.EmailField(required=True)
    days_to_be_used =serializers.IntegerField(required=True)

    def validate(self, attrs):
        days = attrs["days_to_be_used"]
        if days < 1 :
            raise serializers.ValidationError("Day(s) to use borrowed book cannot be less than a 1 or Negative")
        return super().validate(attrs)


