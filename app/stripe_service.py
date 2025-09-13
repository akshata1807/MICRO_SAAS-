import stripe
from flask import current_app


def get_stripe_client():
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    return stripe


def create_checkout_session(customer_email, price_id, success_url, cancel_url):
    client = get_stripe_client()
    session = client.checkout.Session.create(
        payment_method_types=['card'],
        mode='subscription',
        customer_email=customer_email,
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session
