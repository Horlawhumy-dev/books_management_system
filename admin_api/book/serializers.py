from rest_framework import serializers
from .models import AdminBook,User

class AdminBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminBook
        fields = '__all__'

class AdminCreateBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminBook
        fields = '__all__'
        read_only_fields = ["id","borrowed_by","borrowed_until","created_at","updated_at","is_available"]


class UnavailableBooksSerializer(serializers.ModelSerializer):
    available_date = serializers.DateTimeField(read_only=True,source='borrowed_until')
    class Meta:
        model = AdminBook
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id",'email', 'first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id",'email', 'first_name', 'last_name','external_id']


class UsersAndBorrowedBooksSerializer(serializers.Serializer):
    user = UserSerializer()
    books_borrowed = AdminBookSerializer(many=True)


   