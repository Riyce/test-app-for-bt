from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class City(models.Model):
    name = models.CharField(max_length=32, db_index=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='company_owner')
    name = models.CharField(max_length=64, db_index=True, unique=True)
    phone = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    discription = models.TextField()
    foundation_date = models.DateField()
    adress = models.CharField(max_length=128)
    city = models.ForeignKey(City, on_delete=models.CASCADE,
                             related_name='companies')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=128)
    body = models.TextField()
    pub_date = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='news')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Profile(models.Model):
    class Role(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        OWNER = 'owner'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL,
                                related_name='staff', null=True, blank=True)
    role = models.TextField(
        verbose_name='role',
        choices=Role.choices,
        default='user'
    )

    def __str__(self):
        return self.user.username

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_staff(self):
        return self.is_owner or self.is_moderator


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
