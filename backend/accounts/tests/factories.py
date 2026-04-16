"""Factory Boy factories for accounts models."""
import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.local')
    password = factory.PostGenerationMethodCall('set_password', 'TestPass12345!')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    user_type = 'student'
    is_active = True


class AdminFactory(UserFactory):
    username = factory.Sequence(lambda n: f'admin_{n}')
    user_type = 'admin'
    is_staff = True
    is_superuser = True
