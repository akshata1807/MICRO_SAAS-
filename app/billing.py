from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.stripe_service import create_checkout_session
import hashlib
import hmac
import json
import base64
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/subscribe', methods=['GET'])
@login_required
def subscribe():
    return render_template(
        'subscribe.html',
        stripe_pub_key=current_app.config.get('STRIPE_PUBLISHABLE_KEY'),
        stripe_price_basic='price_for_99_rs_plan',
        stripe_price_pro='price_for_299_rs_plan',
        stripe_price_premium='price_for_premium_plan',
        razorpay_key=current_app.config.get('RAZORPAY_KEY_ID'),
        rz_plan_basic=current_app.config.get('RAZORPAY_PLAN_BASIC'),
        rz_plan_pro=current_app.config.get('RAZORPAY_PLAN_PRO'),
        rz_plan_premium=current_app.config.get('RAZORPAY_PLAN_PREMIUM')
    )


@billing_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout():
    price_id = request.form.get('price_id') or request.json.get('price_id') if request.is_json else None
    if not price_id:
        return { 'error': 'Subscription plan not selected' }, 400

    success_url = url_for('billing.subscription_success', _external=True)
    cancel_url = url_for('billing.subscribe', _external=True)
    try:
        session = create_checkout_session(current_user.email, price_id, success_url, cancel_url)
        return { 'sessionId': session.id }, 200
    except Exception as e:
        return { 'error': str(e) }, 400


@billing_bp.route('/subscription-success', methods=['GET'])
@login_required
def subscription_success():
    flash('Subscription successful! Welcome to premium features.', 'success')
    return render_template('subscribe_success.html')


# Razorpay: Create order
@billing_bp.route('/razorpay/create-order', methods=['POST'])
@login_required
def razorpay_create_order():
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        return { 'error': 'Razorpay keys not configured' }, 500

    # Expect amount in INR paise and plan name
    payload = request.get_json(silent=True) or {}
    amount = int(payload.get('amount', 0))
    plan = (payload.get('plan') or 'basic').lower()
    if amount <= 0:
        return { 'error': 'Invalid amount' }, 400

    data = {
        'amount': amount,  # in paise
        'currency': 'INR',
        'receipt': f'rcpt_{current_user.id}_{plan}',
        'notes': {'plan': plan, 'user_id': str(current_user.id)}
    }

    try:
        auth_bytes = f"{key_id}:{key_secret}".encode('utf-8')
        auth_header = base64.b64encode(auth_bytes).decode('utf-8')
        req = Request(
            'https://api.razorpay.com/v1/orders',
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            return json.loads(body), 200
    except HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
        except Exception:
            err_body = str(e)
        return { 'error': err_body }, 400
    except URLError as e:
        return { 'error': str(e) }, 400


# Razorpay: Verify payment signature
@billing_bp.route('/razorpay/verify', methods=['POST'])
@login_required
def razorpay_verify():
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    payload = request.get_json(silent=True) or {}
    order_id = payload.get('razorpay_order_id')
    payment_id = payload.get('razorpay_payment_id')
    signature = payload.get('razorpay_signature')
    if not (order_id and payment_id and signature):
        return { 'error': 'Missing verification fields' }, 400

    body = f"{order_id}|{payment_id}".encode('utf-8')
    expected = hmac.new(key_secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    if hmac.compare_digest(expected, signature):
        # Mark subscription active for current_user in DB if needed
        return { 'status': 'verified' }, 200
    return { 'error': 'Signature mismatch' }, 400


# Razorpay Subscriptions: create subscription (recurring)
@billing_bp.route('/razorpay/create-subscription', methods=['POST'])
@login_required
def razorpay_create_subscription():
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        return { 'error': 'Razorpay keys not configured' }, 500

    payload = request.get_json(silent=True) or {}
    plan = (payload.get('plan') or 'basic').lower()
    plan_map = {
        'basic': current_app.config.get('RAZORPAY_PLAN_BASIC'),
        'pro': current_app.config.get('RAZORPAY_PLAN_PRO'),
        'premium': current_app.config.get('RAZORPAY_PLAN_PREMIUM')
    }
    plan_id = plan_map.get(plan)
    if not plan_id:
        return { 'error': 'Plan not configured' }, 400

    data = {
        'plan_id': plan_id,
        'customer_notify': 1,
        'total_count': 12,  # 12 billing cycles
        'notes': {'user_id': str(current_user.id), 'plan': plan}
    }

    try:
        auth_bytes = f"{key_id}:{key_secret}".encode('utf-8')
        auth_header = base64.b64encode(auth_bytes).decode('utf-8')
        req = Request(
            'https://api.razorpay.com/v1/subscriptions',
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            return json.loads(body), 200
    except HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
        except Exception:
            err_body = str(e)
        return { 'error': err_body }, 400
    except URLError as e:
        return { 'error': str(e) }, 400


# Razorpay Subscriptions: verify signature
@billing_bp.route('/razorpay/verify-subscription', methods=['POST'])
@login_required
def razorpay_verify_subscription():
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    payload = request.get_json(silent=True) or {}
    subscription_id = payload.get('razorpay_subscription_id')
    payment_id = payload.get('razorpay_payment_id')
    signature = payload.get('razorpay_signature')
    if not (subscription_id and payment_id and signature):
        return { 'error': 'Missing verification fields' }, 400

    body = f"{payment_id}|{subscription_id}".encode('utf-8')
    expected = hmac.new(key_secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    if hmac.compare_digest(expected, signature):
        # Mark subscription active in DB
        return { 'status': 'verified' }, 200
    return { 'error': 'Signature mismatch' }, 400
