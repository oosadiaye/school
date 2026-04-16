"""Factory Boy factories for library models."""
import datetime
from decimal import Decimal

import factory
from accounts.tests.factories import UserFactory
from library.models import Author, Book, BookLoan, Category, LibraryMember, Reservation


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f'Author {n}')
    bio = 'A prolific writer.'


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    description = 'A book category.'


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    isbn = factory.Sequence(lambda n: f'978-0-{n:07d}')
    title = factory.Sequence(lambda n: f'Book Title {n}')
    category = factory.SubFactory(CategoryFactory)
    publisher = 'Test Publisher'
    publication_year = 2024
    total_copies = 3
    available_copies = 3
    is_active = True


class LibraryMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LibraryMember

    user = factory.SubFactory(UserFactory)
    member_type = 'student'
    library_card_number = factory.Sequence(lambda n: f'LIB-{n:06d}')
    expiry_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=365)
    )
    is_active = True


class BookLoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookLoan

    book = factory.SubFactory(BookFactory)
    member = factory.SubFactory(LibraryMemberFactory)
    due_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=14)
    )
    status = 'borrowed'
    fine_amount = Decimal('0.00')


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    book = factory.SubFactory(BookFactory)
    member = factory.SubFactory(LibraryMemberFactory)
    status = 'pending'
