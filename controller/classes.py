"""
This file contains all the HTTP routes for classes from the IGSN model, such as Samples and the Sample Register
"""
from flask import Blueprint, request, Response, render_template
import _config as config
import pyldapi
import requests
from io import BytesIO
from lxml import etree
from model.sample import SampleRenderer
from model.site import SiteRenderer
from model.survey import SurveyRenderer


classes = Blueprint('classes', __name__)


def _get_items(page, per_page, elem_tag):
    items = []

    r = None
    if elem_tag == 'IGSN':
        r = requests.get(config.XML_API_URL_SAMPLESET.format(page, per_page), timeout=3)
    elif elem_tag == 'ENO':
        r = requests.get(config.XML_API_URL_SITESET.format(page, per_page), timeout=3)
    elif elem_tag == 'SURVEYID':
        r = requests.get(config.XML_API_URL_SURVEY_REGISTER.format(page, per_page), timeout=3)
    else:
        print('Invalid tag')
        return None

    xml = r.content

    parser = etree.XMLParser(dtd_validation=False)

    try:
        etree.fromstring(xml, parser)
        xml = BytesIO(xml)

        labels = {
            'IGSN': 'Sample ',
            'ENO': 'Site ',
            'SURVEYID': 'Survey '
        }
        for event, elem in etree.iterparse(xml):
            if elem.tag == elem_tag:
                items.append((elem.text, labels[elem.tag] + elem.text))

        return items
    except Exception:
        print('not valid xml')
        return None

@classes.route('/index')
def index():

 return render_template(
        'index.html'
       #api_endpoint=config.API_ENDPOINT
    )

@classes.route('/sample/<string:igsn>')
def sample(igsn):
    """
    A single Sample

    :return: HTTP Response
    """
    s = SampleRenderer(request)
    return s.render()


@classes.route('/sample/<string:igsn>/pingback', methods=['GET', 'POST'])
def sample_pingback(igsn):
    if request.method == 'GET':
        return Response(
            'This endpoint is the individual PROV "pingback" endpoint for Sample {}. It is expected to be used in '
            'accordance with the PROV-AQ Working Group Note (https://www.w3.org/TR/prov-aq/).'.format(igsn),
            mimetype='text/plain'
        )

    # TODO: validate the pingback
    valid = True
    if valid:
        return Response(
            'This is a test response, no action has been taken with the pingback information',
            status=204,
            mimetype='text/plain'
        )
    else:
        return Response(
            'The pingback message submitted is not valid',
            status=400,
            mimetype='text/plain'
        )


@classes.route('/sample/')
def samples():
    """
    The Register of Samples

    :return: HTTP Response
    """

    # get the total register count from the XML API
    try:
        r = requests.get(config.XML_API_URL_TOTAL_COUNT)
        no_of_items = int(r.content.decode('utf-8').split('<RECORD_COUNT>')[1].split('</RECORD_COUNT>')[0])

        page = request.values.get('page') if request.values.get('page') is not None else 1
        per_page = request.values.get('per_page') if request.values.get('per_page') is not None else 20
        items = _get_items(page, per_page, "IGSN")
    except Exception as e:
        print(e)
        return Response('The Samples Register is offline', mimetype='text/plain', status=500)

    r = pyldapi.RegisterRenderer(
        request,
        request.url,
        'Sample Register',
        'A register of Samples',
        items,
        [config.URI_SAMPLE_CLASS],
        no_of_items
    )

    return r.render()


@classes.route('/site/ga/<string:site_no>')
def site(site_no):
    s = SiteRenderer(request)
    return s.render()


@classes.route('/site/ga/')
def sites():
    # get the total register count for site
    try:
        r = requests.get(config.XML_API_URL_SITES_TOTAL_COUNT)
        no_of_items = int(r.content.decode('utf-8').split('<RECORDS>')[1].split('</RECORDS>')[0])
        # no_of_items =

        page = request.values.get('page') if request.values.get('page') is not None else 1
        per_page = request.values.get('per_page') if request.values.get('per_page') is not None else 20
        items = _get_items(page, per_page, "ENO")
    except Exception as e:
        print(e)
        return Response('The Site Register is offline', mimetype='text/plain', status=500)

    r = pyldapi.RegisterRenderer(
        request,
        request.url,
        'Site Register',
        'A register of Sites',
        items,
        [config.URI_SITE_CLASS],
        no_of_items
    )

    return r.render()


@classes.route('/survey/ga/')
def surveys():
    # get the total register count for survey
    try:
        no_of_items = 9200 #TODO: implement a survey count in Oracle XML API
        page = request.values.get('page') if request.values.get('page') is not None else 1
        per_page = request.values.get('per_page') if request.values.get('per_page') is not None else 20
        items = _get_items(page, per_page, "SURVEYID")
    except Exception as e:
        print(e)
        return Response('The Survey Register is offline', mimetype='text/plain', status=500)

    r = pyldapi.RegisterRenderer(
        request,
        request.url,
        'Survey Register',
        'A register of Surveys',
        items,
        [config.URI_SURVEY_CLASS],
        no_of_items
    )
    return r.render()


@classes.route('/survey/ga/<string:survey_no>')
def survey(survey_no):
    s = SurveyRenderer(request)
    return s.render()
