import uuid
import hashlib
import hmac
import requests
from django.conf import settings
from decimal import Decimal

class PaymentGateway:
    """Payment Gateway Integration - Supports Paystack, Flutterwave, Stripe"""
    
    def __init__(self, provider='paystack'):
        self.provider = provider
        if provider == 'paystack':
            self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', 'sk_test_xxx')
            self.public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', 'pk_test_xxx')
            self.base_url = 'https://api.paystack.co'
        elif provider == 'flutterwave':
            self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', 'xxx')
            self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', 'xxx')
            self.base_url = 'https://api.flutterwave.com/v3'
        elif provider == 'stripe':
            self.secret_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_xxx')
            self.public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_xxx')
            self.base_url = 'https://api.stripe.com/v1'
    
    def initialize_transaction(self, email, amount, callback_url, reference=None):
        """Initialize a payment transaction"""
        if not reference:
            reference = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        amount_kobo = int(Decimal(str(amount)) * 100)
        
        if self.provider == 'paystack':
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'email': email,
                'amount': amount_kobo,
                'reference': reference,
                'callback_url': callback_url,
                'currency': 'NGN'
            }
            response = requests.post(f'{self.base_url}/transaction/initialize', json=data, headers=headers)
            result = response.json()
            if result.get('status'):
                return {
                    'success': True,
                    'reference': reference,
                    'authorization_url': result['data']['authorization_url'],
                    'access_code': result['data'].get('access_code'),
                    'transaction_id': result['data'].get('id')
                }
            return {'success': False, 'message': result.get('message', 'Payment initialization failed')}
        
        elif self.provider == 'flutterwave':
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'tx_ref': reference,
                'amount': str(amount),
                'currency': 'NGN',
                'redirect_url': callback_url,
                'customer': {'email': email}
            }
            response = requests.post(f'{self.base_url}/payments', json=data, headers=headers)
            result = response.json()
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'reference': reference,
                    'authorization_url': result['data']['link'],
                    'transaction_id': result['data'].get('id')
                }
            return {'success': False, 'message': result.get('message', 'Payment initialization failed')}
        
        elif self.provider == 'stripe':
            import stripe
            stripe.api_key = self.secret_key
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'ngn',
                            'product_data': {'name': 'School Fees'},
                            'unit_amount': amount_kobo,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=callback_url + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=callback_url,
                    metadata={'reference': reference}
                )
                return {
                    'success': True,
                    'reference': reference,
                    'authorization_url': session.url,
                    'transaction_id': session.id
                }
            except Exception as e:
                return {'success': False, 'message': str(e)}
        
        return {'success': False, 'message': 'Unknown provider'}
    
    def verify_transaction(self, reference):
        """Verify a payment transaction"""
        if self.provider == 'paystack':
            headers = {'Authorization': f'Bearer {self.secret_key}'}
            response = requests.get(f'{self.base_url}/transaction/verify/{reference}', headers=headers)
            result = response.json()
            if result.get('status') and result['data'].get('status') == 'success':
                return {
                    'success': True,
                    'verified': True,
                    'amount': result['data']['amount'] / 100,
                    'reference': result['data']['reference'],
                    'transaction_id': result['data'].get('id'),
                    'customer_email': result['data'].get('customer', {}).get('email'),
                    'payment_method': result['data'].get('authorization', {}).get('channel')
                }
            return {'success': False, 'verified': False, 'message': 'Transaction verification failed'}
        
        elif self.provider == 'flutterwave':
            headers = {'Authorization': f'Bearer {self.secret_key}'}
            response = requests.get(f'{self.base_url}/transactions/{reference}/verify', headers=headers)
            result = response.json()
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'verified': True,
                    'amount': result['data']['amount'],
                    'reference': result['data']['tx_ref'],
                    'transaction_id': result['data'].get('id'),
                    'customer_email': result['data'].get('customer', {}).get('email'),
                    'payment_method': result['data'].get('payment_type')
                }
            return {'success': False, 'verified': False, 'message': 'Transaction verification failed'}
        
        elif self.provider == 'stripe':
            import stripe
            stripe.api_key = self.secret_key
            try:
                session = stripe.checkout.Session.retrieve(reference)
                if session.payment_status == 'paid':
                    return {
                        'success': True,
                        'verified': True,
                        'amount': session.amount_total / 100,
                        'reference': session.metadata.get('reference', reference),
                        'transaction_id': session.id,
                        'customer_email': session.customer_email,
                        'payment_method': 'card'
                    }
                return {'success': False, 'verified': False, 'message': 'Payment not completed'}
            except Exception as e:
                return {'success': False, 'verified': False, 'message': str(e)}
        
        return {'success': False, 'verified': False, 'message': 'Unknown provider'}
    
    def refund(self, transaction_id, amount=None):
        """Process a refund"""
        if self.provider == 'paystack':
            headers = {'Authorization': f'Bearer {self.secret_key}', 'Content-Type': 'application/json'}
            data = {'transaction': transaction_id}
            if amount:
                data['amount'] = int(Decimal(str(amount)) * 100)
            response = requests.post(f'{self.base_url}/refund', json=data, headers=headers)
            return response.json().get('status', False)
        
        elif self.provider == 'flutterwave':
            headers = {'Authorization': f'Bearer {self.secret_key}', 'Content-Type': 'application/json'}
            data = {'transaction_id': transaction_id}
            if amount:
                data['amount'] = str(amount)
            response = requests.post(f'{self.base_url}/refunds', json=data, headers=headers)
            return response.json().get('status', False)
        
        return False


def generate_payment_link(invoice, provider='paystack'):
    """Helper function to generate payment link for an invoice"""
    gateway = PaymentGateway(provider)
    student = invoice.student
    email = student.user.email if student.user else f"{student.matric_number}@student.edu"
    amount = float(invoice.balance)
    callback_url = getattr(settings, 'PAYMENT_CALLBACK_URL', 'http://localhost:5173/payment/callback')
    
    result = gateway.initialize_transaction(
        email=email,
        amount=amount,
        callback_url=callback_url,
        reference=f"INV-{invoice.id}-{uuid.uuid4().hex[:8].upper()}"
    )
    return result
