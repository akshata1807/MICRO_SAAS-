from flask import request, jsonify, current_app, url_for, redirect
from app.stripe_service import create_checkout_session
import stripe

@main_bp.route('/subscribe', methods=['GET'])
@login_required
def subscribe():
    # Provide subscription options (display UI)
    return render_template('subscribe.html', stripe_pub_key=current_app.config['STRIPE_PUBLISHABLE_KEY'])

@main_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout():
    price_id = request.form.get('price_id')  # Pass selected plan price id
    if not price_id:
        flash("Subscription plan not selected", "danger")
        return redirect(url_for('main.subscribe'))

    success_url = url_for('main.subscription_success', _external=True)
    cancel_url = url_for('main.subscribe', _external=True)
    try:
        session = create_checkout_session(current_user.email, price_id, success_url, cancel_url)
        return redirect(session.url, code=303)
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for('main.subscribe'))

@main_bp.route('/subscription-success')
@login_required
def subscription_success():
    flash('Subscription successful! Welcome to premium features.', 'success')
    return render_template('subscription_success.html')
