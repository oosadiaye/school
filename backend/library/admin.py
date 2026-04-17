from django.contrib import admin

from .models import Author, Book, BookLoan, Category, LibraryMember, Reservation


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "category", "total_copies", "available_copies", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "isbn")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("title",)


@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ("library_card_number", "user", "member_type", "join_date", "is_active")
    list_filter = ("member_type", "is_active")
    search_fields = ("user__username", "library_card_number")
    readonly_fields = ("join_date", "created_at")
    ordering = ("-join_date",)


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "borrow_date", "due_date", "status", "fine_amount")
    list_filter = ("status",)
    search_fields = ("book__title", "member__library_card_number")
    readonly_fields = ("borrow_date", "created_at")
    ordering = ("-borrow_date",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "status", "reserved_date", "created_at")
    list_filter = ("status",)
    search_fields = ("book__title", "member__library_card_number")
    readonly_fields = ("reserved_date", "created_at")
    ordering = ("-reserved_date",)
