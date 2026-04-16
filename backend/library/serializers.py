from rest_framework import serializers
from .models import Author, Category, Book, LibraryMember, BookLoan, Reservation

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class BookSerializer(serializers.ModelSerializer):
    author_names = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'authors', 'author_names', 'category', 'category_name',
                  'publisher', 'publication_year', 'edition', 'total_copies', 'available_copies',
                  'shelf_location', 'description', 'is_active', 'created_at']
    
    def get_author_names(self, obj):
        return [a.name for a in obj.authors.all()]

class LibraryMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = LibraryMember
        fields = ['id', 'user', 'user_name', 'member_type', 'library_card_number',
                  'join_date', 'expiry_date', 'is_active', 'created_at']

class BookLoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = BookLoan
        fields = ['id', 'book', 'book_title', 'member', 'member_name', 'borrow_date',
                  'due_date', 'return_date', 'status', 'fine_amount', 'created_at']

class ReservationSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'book', 'book_title', 'member', 'member_name',
                  'reserved_date', 'status', 'fulfilled_date', 'created_at']
