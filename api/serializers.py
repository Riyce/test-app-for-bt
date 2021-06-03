from rest_framework import serializers

from companies.models import City, Company, News, Profile


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'body')
        model = News


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = News


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'phone', 'email', 'discription',
                  'foundation_date', 'adress', 'city')
        model = Company


class CompanyListSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(
        queryset=City.objects.all(),
        slug_field='name',
    )
    news = NewsSerializer(many=True)

    class Meta:
        fields = ('name', 'phone', 'email', 'discription',
                  'foundation_date', 'adress', 'city', 'news')
        model = Company


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    role = serializers.ChoiceField(choices=['moderator', 'user'])

    class Meta:
        model = Profile
        fields = ('user', 'role')
