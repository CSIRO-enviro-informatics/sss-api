# this set of tests calls a series of endpoints that this API is meant to expose and tests them for content
import requests
import re
import pytest
import pprint as pp

SYSTEM_URI = 'http://localhost:5000'
HEADERS_TTL = {'Accept': 'text/turtle'}
HEADERS_HTML = {'Accept': 'text/html'}


def valid_endpoint_content(uri, pattern, error_msg, headers=None, print_out=False, allow_redirects=True):
    # dereference the URI
    r = requests.get(uri, headers=headers, allow_redirects=allow_redirects)
    if print_out:
        pp.pprint(r.content)
    # parse the content looking for the thing specified in REGEX
    if re.search(pattern, r.content.decode('utf-8'), re.MULTILINE):
        return True
    else:
        pp.pprint(error_msg)
        return False


def test_landing_page_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}',
        r'<h1>Sites, Samples Surveys Linked Data API<\/h1>',
        'SSS landing page failed'
    )


def test_about_page_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/about',
        r'<h2>About<\/h2>',
        'SSS about page failed'
    )


def test_oai_endpoint():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/oai', #TODO: Make an actual request by supplying a verb
        r'<error code="badVerb">You did not specify an OAI verb<\/error>',
        'SSS OAI endpoint failed'
    )


def test_sample_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/',
        r'<h1>Sample Register<\/h1>',
        'SSS API Sample Register html failed'
    )


@pytest.mark.skip('SSS API Sample Register rdf turtle file extension not yet implemented')
def test_sample_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/index.ttl',
        r'<AU1> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample> ;',
        'SSS API Sample Register rdf turtle file extension failed'
    )


def test_sample_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_format=text/turtle',
        r'<AU1> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample> ;',
        'SSS API Sample Register rdf turtle qsa failed'
    )


def test_sample_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/',
        r'<AU1> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample> ;',
        'SSS API Sample Register rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_register_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=reg&_format=text/html',
        r'<h1>Sample Register<\/h1>',
        'SSS API Sample Register reg view html failed'
    )


def test_sample_register_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=reg&_format=text/turtle',
        r'<AU1> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample> ;',
        'SSS API Sample Register reg view rdf turtle qsa failed'
    )


def test_sample_register_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=reg',
        r'<AU1> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample> ;',
        'SSS API Sample Register reg view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_register_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=alternates&_format=text/html',
        r'<td>A simple list-of-items view taken from the Registry Ontology<\/td>',
        'SSS API Sample Register alternates view html failed'
    )


def test_sample_register_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=alternates&_format=text/turtle',
        r'rdfs:label "Alternates"\^\^xsd:string ;',
        'SSS API Sample Register alternates view rdf turtle qsa failed'
    )


def test_sample_register_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/?_view=alternates',
        r'rdfs:label "Alternates"\^\^xsd:string ;',
        'SSS API Sample Register alternates view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_instance_AU1000012_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012',
        r'<tr><td>IGSN<\/td><td>AU1000012<\/td><\/tr>',
        'SSS API Sample instance AU1000012 html failed'
    )


@pytest.mark.skip('SSS API Sample instance AU1000012 rdf turtle file extension not yet implemented')
def test_sample_instance_AU1000012_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012.ttl',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a samfl:Specimen ;',
        'SSS API Sample instance AU1000012 rdf turtle file extension failed'
    )


def test_sample_instance_AU1000012_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a samfl:Specimen ;',
        'SSS API Sample instance AU1000012 rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a samfl:Specimen ;',
        'SSS API Sample instance AU1000012 rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_instance_AU1000012_igsn_o_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=igsn-o&_format=text/html',
        r'<tr><td>IGSN<\/td><td>AU1000012<\/td><\/tr>',
        'SSS API Sample instance AU1000012 igsn-o view html failed'
    )


def test_sample_instance_AU1000012_igsn_o_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=igsn-o&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a samfl:Specimen ;',
        'SSS API Sample instance AU1000012 igsn-o view rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_igsn_o_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=igsn-o',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a samfl:Specimen ;',
        'SSS API Sample instance AU1000012 igsn-o view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_instance_AU1000012_csirov3_view_xml():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=csirov3&_format=text/xml',
        r'<cs:resourceIdentifier>AU1000012<\/cs:resourceIdentifier>',
        'SSS API Sample instance AU1000012 csirov3 view text/xml failed'
    )


def test_sample_instance_AU1000012_dct_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=dct&_format=text/html',
        r'<tr><th>Title<\/th><td>Sample igsn:AU1000012<\/td><\/tr>',
        'SSS API Sample instance AU1000012 dct view html failed'
    )


def test_sample_instance_AU1000012_dct_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=dct&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a dct:PhysicalResource ;',
        'SSS API Sample instance AU1000012 dct view rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_dct_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=dct',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a dct:PhysicalResource ;',
        'SSS API Sample instance AU1000012 dct view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_sample_instance_AU1000012_igsn_view_xml():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=igsn&_format=text/xml',
        r'<igsn:name>Sample igsn:AU1000012<\/igsn:name>',
        'SSS API Sample instance AU1000012 igsn view text/xml failed'
    )


def test_sample_instance_AU1000012_igsn_r1_view_xml():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=igsn-r1&_format=text/xml',
        r'<igsn:title>Sample igsn:AU1000012<\/igsn:title>',
        'SSS API Sample instance AU1000012 igsn-r1 text/xml failed'
    )


def test_sample_instance_AU1000012_prov_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=prov&_format=text/html',
        r'<h3>PROV data graph<\/h3>',
        'SSS API Sample instance AU1000012 prov view html failed'
    )


def test_sample_instance_AU1000012_prov_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=prov&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a prov:Entity ;',
        'SSS API Sample instance AU1000012 prov view rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_prov_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=prov',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a prov:Entity ;',
        'SSS API Sample instance AU1000012 prov view rdf turtle accept header failed'
    )


def test_sample_instance_AU1000012_sosa_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=sosa&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/sample\/AU1000012> a prov:Entity,',
        'SSS API Sample instance AU1000012 sosa view rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=alternates&_format=text/html',
        r'<td>Version 1 of the official IGSN XML schema<\/td>',
        'SSS API Sample instance AU1000012 alternates view html failed'
    )


def test_sample_instance_AU1000012_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=alternates&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample>',
        'SSS API Sample instance AU1000012 alternates view rdf turtle qsa failed'
    )


def test_sample_instance_AU1000012_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sample/AU1000012?_view=alternates',
        r'<http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/igsn#Sample>',
        'SSS API Sample instance AU1000012 alternates view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/',
        r'<li class="no-line-height"><a href="2">Site 2<\/a><\/li>',
        'SSS API Site Register html failed'
    )


@pytest.mark.skip('SSS API Site Register rdf turtle file extension not yet implemeneted')
def test_site_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/index.ttl',
        r'<10> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/pdm#Site> ;',
        'SSS API Site Register rdf turtle file extension failed'
    )


def test_site_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_format=text/turtle',
        r'<10> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/pdm#Site> ;',
        'SSS API Site Register rdf turtle qsa failed'
    )


def test_site_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/',
        r'<10> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/pdm#Site> ;',
        'SSS API Site Register rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_register_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=reg&_format=text/html',
        r'<li class="no-line-height"><a href="2">Site 2<\/a><\/li>',
        'SSS API Site Register reg view html failed'
    )


def test_site_register_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=reg&_format=text/turtle',
        r'<10> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/pdm#Site> ;',
        'SSS API Site Register reg view rdf turtle qsa failed'
    )


def test_site_register_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=reg',
        r'<10> a <http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/pdm#Site> ;',
        'SSS API Site Register reg view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_register_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=alternates&_format=text/html',
        r'<tr><th>View<\/th><th>Formats<\/th><th>View Desc\.<\/th><th>View Namespace<\/th><\/tr>',
        'SSS API Site Register alternates view html failed'
    )


def test_site_register_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=alternates&_format=text/turtle',
        r'rdfs:comment "The view that lists all other views"\^\^xsd:string ;',
        'SSS API Site Register alternates view rdf turtle qsa failed',
    )


def test_site_register_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/?_view=alternates',
        r'rdfs:comment "The view that lists all other views"\^\^xsd:string ;',
        'SSS API Site Register alternates view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_instance_21_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21',
        r'<tr><td>Description<\/td><td>LUSIAD Leg 6C, Argo<\/td><\/tr>',
        'SSS API Site instance 21 html failed'
    )


@pytest.mark.skip('SSS API Site instance 21 rdf turtle fiel extension not yet implemented')
def test_site_instance_21_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21.ttl',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> a <http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey>,',
        'SSS API Site instance 21 rdf turtle file extension failed'
    )


def test_site_instance_21_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> a <http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey>,',
        'SSS API Site instance 21 rdf turtle qsa failed'
    )


def test_site_instance_21_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> a <http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey>,',
        'SSS API Site instance 21 rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_instance_21_pdm_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=pdm&_format=text/html',
        r'<tr><td>Description<\/td><td>LUSIAD Leg 6C, Argo<\/td><\/tr>',
        'SSS API Site instance 21 pdm view html failed'
    )


def test_site_instance_21_pdm_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=pdm&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> a <http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey>,',
        'SSS API Site instance 21 pdm view rdf turtle qsa failed'
    )


def test_site_instance_21_pdm_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=pdm',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> a <http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey>,',
        'SSS API Site instance 21 pdm view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_site_instance_21_nemsr_view_geo_json():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=nemsr&_format=application/vnd.geo+json',
        r'"properties": {"network": {}},',
        'SSS API Site instance 21 nemsr view application/vnd.geo+json failed'
    )


def test_site_instanace_21_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=alternates&_format=text/html',
        r'<h3>Alternates view of a <a href="http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey">http:\/\/pid\.geoscience\.gov\.au\/def\/voc\/ga\/featureofinteresttype\/survey<\/a><\/h3>',
        'SSS API Site instance 21 alternates view html failed'
    )


def test_site_instanace_21_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=alternates&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> alt:hasDefaultView',
        'SSS API Site instance 21 alternates view rdf turtle qsa failed'
    )


def test_site_instanace_21_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/site/21?_view=alternates',
        r'<http:\/\/pid\.geoscience\.gov\.au\/site\/ga\/21> alt:hasDefaultView',
        'SSS API Site instance 21 alternates view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/',
        r'<li class="no-line-height"><a href="01020013">Survey 01020013<\/a><\/li>',
        'SSS API Survey Register html failed'
    )


@pytest.mark.skip('SSS API Survey Register rdf turtle file extension not yet implemented')
def test_survey_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/index.ttl',
        r'<01020013> a <http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/> ;',
        'SSS API Survey Register rdf turtle file extension failed'
    )


def test_survey_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_format=text/turtle',
        r'<01020013> a <http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/> ;',
        'SSS API Survey Register rdf turtle qsa failed'
    )


def test_survey_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/',
        r'<01020013> a <http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/> ;',
        'SSS API Survey Register rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_register_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=reg&_format=text/html',
        r'<li class="no-line-height"><a href="01020013">Survey 01020013<\/a><\/li>',
        'SSS API Survey Register reg view html failed'
    )


def test_survey_register_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=reg&_format=text/turtle',
        r'<01020013> a <http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/> ;',
        'SSS API Survey Register reg view rdf turtle qsa failed'
    )


def test_survey_register_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=reg',
        r'<01020013> a <http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/> ;',
        'SSS API Survey Register reg view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_register_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=alternates&_format=text/html',
        r'<tr><th>View<\/th><th>Formats<\/th><th>View Desc\.<\/th><th>View Namespace<\/th><\/tr>',
        'SSS API Survey Register alternates view html'
    )


def test_survey_register_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=alternates&_format=text/turtle',
        r'rdfs:comment "A simple list-of-items view taken from the Registry Ontology"\^\^xsd:string ;',
        'SSS API Survey Register alternates view rdf turtle qsa'
    )


def test_survey_register_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/?_view=alternates',
        r'rdfs:comment "A simple list-of-items view taken from the Registry Ontology"\^\^xsd:string ;',
        'SSS API Survey Register alternates view rdf turtle accept header',
        headers=HEADERS_TTL
    )


def test_survey_instance_01020035_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035',
        r'<tr><td>ID<\/td><td>01020035<\/td><\/tr>',
        'SSS API Survey instance 01020035 html failed'
    )


@pytest.mark.skip('SSS API Survey instance 01020035 rdf turtle file extension not yet implemented')
def test_survey_instance_01020035_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035.ttl',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a gapd:PublicSurvey,',
        'SSS API Survey instance 01020035 rdf turtle file extension failed'
    )


def test_survey_instance_01020035_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a gapd:PublicSurvey,',
        'SSS API Survey instance 01020035 rdf turtle qsa failed'
    )


def test_survey_instance_01020035_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a gapd:PublicSurvey,',
        'SSS API Survey instance 01020035 rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_instance_01020035_gapd_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=gapd&_format=html',
        r'<tr><td>ID<\/td><td>01020035<\/td><\/tr>',
        'SSS API Survey instance 01020035 gapd view html failed'
    )


def test_survey_instance_01020035_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=gapd&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a gapd:PublicSurvey,',
        'SSS API Survey instance 01020035 gapd rdf turtle qsa failed'
    )


def test_survey_instance_01020035_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=gapd',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a gapd:PublicSurvey,',
        'SSS API Survey instance 01020035 gapd rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_instance_01020035_argus_view_xml():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=argus&_format=text/xml',
        r'<SURVEYNAME>Eltanin Cruise 35<\/SURVEYNAME>',
        'SSS API Survey instance 01020035 argus view text/xml failed'
    )


def test_survey_instance_01020035_sosa_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=sosa&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/feature\/earthSusbsurface> rdfs:label "Earth Subsurface"\^\^xsd:string ;',
        'SSS API Survey instance 01020035 sosa view rdf turtle qsa'
    )


def test_survey_instance_01020035_sosa_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=sosa',
        r'<http:\/\/pid\.geoscience\.gov\.au\/feature\/earthSusbsurface> rdfs:label "Earth Subsurface"\^\^xsd:string ;',
        'SSS API Survey instance 01020035 sosa view rdf turtle accept header',
        headers=HEADERS_TTL
    )


def test_survey_instance_01020035_prov_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=prov&_format=text/html',
        r'<h1>Survey 01020035<\/h1>',
        'SSS API Survey instance 01020035 prov view html failed'
    )


def test_survey_instance_01020035_prov_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=prov&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a prov:Activity ;',
        'SSS API Survey instance 01020035 prov view rdf turtle qsa failed'
    )


def test_survey_instance_01020035_prov_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=prov',
        r'<http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035> a prov:Activity ;',
        'SSS API Survey instance 01020035 prov view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


def test_survey_instance_01020035_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=alternates&_format=text/html',
        r'<h3>Instance <a href="http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035">http:\/\/pid\.geoscience\.gov\.au\/survey\/ga\/01020035<\/a><\/h3>',
        'SSS API Survey instance 01020035 alternates view html failed'
    )


def test_survey_instance_01020035_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=alternates&_format=text/turtle',
        r'<http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/testing#Survey> alt:hasDefaultView',
        'SSS API Survey instance 01020035 alternates view rdf turtle qsa failed'
    )


def test_survey_instance_01020035_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/survey/01020035?_view=alternates',
        r'<http:\/\/pid\.geoscience\.gov\.au\/def\/ont\/ga\/testing#Survey> alt:hasDefaultView',
        'SSS API Survey instance 01020035 alternates view rdf turtle accept header failed',
        headers=HEADERS_TTL
    )


if __name__ == '__main__':
    pass