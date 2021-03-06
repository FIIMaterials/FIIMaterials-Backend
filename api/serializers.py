from rest_framework import serializers
from api.models import Link, Class, Student, Resource, Feedback, ClassRating, About, Credits, Asset
import re
from api.utils import random_token, sendemail


class CreditsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Credits
    fields = ['id', 'name', 'about', 'link', 'role', 'image_link']


class AboutSerializer(serializers.ModelSerializer):
  class Meta:
    model = About
    fields = ['id', 'title', 'body']


class LinkSerializer(serializers.ModelSerializer):
  class Meta:
    model = Link
    fields = ['name', 'link']


class ClassSerializer(serializers.ModelSerializer):
  class Meta:
    model = Class
    fields = ['id', 'name', 'name_short', 'average_rating', 'credits', 'year', 'semester', 'about',
              'material_link', 'site_link', 'site_password', 'votes_number']


class AssetSerializer(serializers.ModelSerializer):
  class Meta:
    model = Asset
    fields = ['id', 'name', 'content']


class SignupStudentSerializer(serializers.ModelSerializer):
  re_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

  class Meta:
    model = Student
    fields = ['username', 'email', 'password', 're_password']
    extra_kwargs = {
      'password': {'write_only': True},
    }

  def create(self, validated_data):

    password = validated_data['password']
    re_password = validated_data['re_password']

    if password != re_password:
      raise serializers.ValidationError({'password': 'The password must match'})

    student = Student(
      username=validated_data['username'],
      email=validated_data['email'],
    )
    student.set_password(password)
    student.save()

    verification_token = random_token(16)

    from api.models import VerificationToken
    VerificationToken(student=student, token=verification_token, type=1).save()

    email_context = {
      'token': verification_token,
      'username': student.username,
    }

    sendemail(subject='Account Verification FIIMaterials', template='email_verification.html',
              context=email_context, email_to=[student.email])

    return student


class LoginStudentSerializer(serializers.Serializer):
  username_email = serializers.CharField(max_length=50)
  password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

  EMAIL_REGEX = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

  def create(self, validated_data):
    identifier = validated_data['username_email']  # username or password
    password = validated_data['password']
    student = None

    email_pattern = re.compile(self.EMAIL_REGEX)
    if email_pattern.match(identifier):
      student = Student.objects.get(email=identifier)
    else:
      student = Student.objects.get(username=identifier)

    if student is None:
      raise serializers.ValidationError("User don't exist")

    if not student.check_password(password):
      raise serializers.ValidationError("The password is wrong")

    if not student.is_active:
      raise serializers.ValidationError("Account is not activated")

    return student

  def update(self, instance, validated_data):
    pass


class ResourceSerializer(serializers.ModelSerializer):

  class Meta:
    model = Resource
    fields = ['id', 'title', 'description', 'image_url', 'link_url', 'tag_list']


class FeedbackSerializer(serializers.ModelSerializer):

  class Meta:
    model = Feedback
    fields = ['id', 'student', 'name', 'show_name', 'implemented', 'feedback', 'date_created']


class ClassRatingSerializer(serializers.ModelSerializer):

  class Meta:
    model = ClassRating
    fields = ['student', 'class_name', 'rating']
