"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
from flask import Blueprint, render_template, request
import _config as config
import yaml
import os

pages = Blueprint('controller', __name__)

d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = "{}/_config/home_page_settings.yml".format(d)

#print(os.path.relpath(os.path.abspath(__file__)))
yaml_data = yaml.safe_load(open(path))
home_page_boxes_dict = yaml_data['home_page_boxes']

@pages.route('/')
def index():
    """
    A basic landing page for this web service
    :return: HTTP Response (HTML page only)
    """
    rule = request.url_rule
    return render_template(
        'new_home2.html',
        api_endpoint=config.BASE_URL,
        home_page_settings=home_page_boxes_dict
    )


@pages.route('/about')
def about():
    return render_template(
        'page_about.html'
    )

