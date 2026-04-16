"""Base service pattern documentation.

All Django app `services.py` modules in this project follow these conventions:

1. Services are stateless — no instance state. Prefer `@staticmethod`.
2. Services raise `DomainError` subclasses for business-rule violations.
   The custom DRF exception handler (see `core.exceptions`) turns these
   into standardized JSON responses.
3. Multi-step DB operations must be wrapped in `transaction.atomic`.
4. Every public service method has a docstring describing inputs, outputs,
   and raised exceptions.
5. Every public service method has at least one test in
   `<app>/tests/test_services.py`.

Example:
    from django.db import transaction
    from core.exceptions import ConflictError

    class InvoiceService:
        @staticmethod
        def generate_for_student(student, session, by):
            '''Generate all invoices for a student for a given session.

            Args:
                student: Student instance
                session: AcademicSession instance
                by: User performing the action (for audit)

            Returns:
                list[Invoice] — freshly created invoices

            Raises:
                ConflictError: if any invoice already exists
                NotFound: if no FeeStructure matches
            '''
            with transaction.atomic():
                # business logic here
                ...

This module intentionally has no classes; it exists to document the pattern.
"""
