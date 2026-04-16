from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from finance.models import FeeStructure, Invoice
from datetime import datetime

@receiver(post_save, sender=Student)
def create_invoices_on_registration(sender, instance, created, **kwargs):
    """Create invoices automatically when a new student is registered"""
    if created:
        session = f"{instance.admission_year}/{instance.admission_year + 1}"
        
        fee_structures = FeeStructure.objects.filter(
            programme=instance.programme,
            level=str(instance.level),
            session=session,
            auto_generate=True
        )
        
        for fs in fee_structures:
            invoice, created = Invoice.objects.get_or_create(
                student=instance,
                fee_structure=fs,
                defaults={
                    'amount': fs.amount,
                    'due_date': fs.due_date or datetime.now().date()
                }
            )
            if created:
                print(f"Auto-generated invoice for student {instance.matric_number}: {fs.fee_type.name}")
