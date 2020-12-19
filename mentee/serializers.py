from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from mentee.models import User
from django.core.exceptions import ObjectDoesNotExist



from .models import MentorImage, mentor_schedule, mentor_topics, sales_order, mentor_profile



JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'name')

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)

        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'User with given email does not exists'
            )
        return {
            'id':user.pk,
            'token': jwt_token
        }




class MentorImageSerializer(serializers.HyperlinkedModelSerializer):

    image = serializers.ImageField(max_length= None, use_url=True)
    class Meta:

        model = MentorImage

        fields = [
            'image',
            'mentor_name',
        ]


class mentor_schedule_serializer(serializers.ModelSerializer):

    class Meta:
        model = mentor_schedule

        fields = "__all__"


class sales_order_serializer(serializers.ModelSerializer):

    class Meta:
        model = sales_order

        fields = "__all__"

        


class mentor_topics_serializer(serializers.ModelSerializer):

    class Meta:
        model = mentor_topics

        fields = "__all__"