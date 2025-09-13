from flask import Blueprint, render_template

pages_bp = Blueprint('pages_bp', __name__)

@pages_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@pages_bp.route('/terms')
def terms():
    return render_template('terms.html')

@pages_bp.route('/contact')
def contact():
    return render_template('contact.html')
