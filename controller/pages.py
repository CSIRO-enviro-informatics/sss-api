"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
from flask import Blueprint, render_template, request
import _config as config


pages = Blueprint('controller', __name__)


@pages.route('/')
def index():
    """
    A basic landing page for this web service
    :return: HTTP Response (HTML page only)
    """
    rule = request.url_rule
    print(rule)
    return render_template(
        'page_index.html',
        api_endpoint=config.BASE_URL + '/sss'
    )


@pages.route('/about')
def about():
    return render_template(
        'page_about.html'
    )

