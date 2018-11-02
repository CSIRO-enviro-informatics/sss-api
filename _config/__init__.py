from os.path import dirname, realpath, join, abspath

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

PAGE_SIZE_DEFAULT = 100

GOOGLE_MAPS_API_KEY_EMBED = 'AIzaSyDhuFCoJynhhQT7rcgKYzk3i7K77IEwjO4'
GOOGLE_MAPS_API_KEY = 'AIzaSyCUDcjVRsIHVHpv53r7ZnaX5xzqJbyGk58'

#
# samples
#
XML_API_URL_SAMPLESET = 'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_igsnSampleSet' \
                        '?pOrder=IGSN&pPageNo={0}&pNoOfLinesPerPage={1}'
XML_API_URL_SAMPLE = 'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_igsnSample?pIGSN={0}'

XML_API_URL_SAMPLESET_DATE_RANGE = \
    'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_igsnSampleSet' \
    '?pOrder=IGSN&pPageNo={0}&pNoOfLinesPerPage={1}&pModifiedFromDate={2}' \
    '&pModifiedToDate={3}'

XML_API_URL_MIN_DATE = 'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_Earliest_Date_Modified'
XML_API_URL_TOTAL_COUNT = 'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_Number_Modified'
XML_API_URL_TOTAL_COUNT_DATE_RANGE = 'http://dbforms.ga.gov.au/www_distp/a.igsn_api.get_Number_Modified'\
                                     '?pModifiedFromDate={0}&pModifiedToDate={1}'

ADMIN_EMAIL = 'dataman@ga.gov.au'

REGISTER_BASE_URI = 'http://pid.geoscience.gov.au/sample/'
URI_SAMPLE_CLASS = 'http://pid.geoscience.gov.au/def/ont/ga/igsn#Sample'
URI_SAMPLE_INSTANCE_BASE = 'http://pid.geoscience.gov.au/sample/'
BASE_URI_OAI = 'http://pid.geoscience.gov.au/oai'

OAI_BATCH_SIZE = 1000


#
# sites
#
XML_API_URL_SITESET = 'http://dbforms.ga.gov.au/www/a.entities_api.SearchEntities' \
                        '?pOrder=ENO&pPageNo={0}&pNoOfRecordsPerPage={1}'
XML_API_URL_SITE = 'http://dbforms.ga.gov.au/www/a.entities_api.entities?pEno={0}'
# XML_API_URL_NETWORKSET = ''
# XML_API_URL_NETWORK = ''

XML_API_URL_SITESET_DATE_RANGE = \
    'http://dbforms.ga.gov.au/www/a.entities_api.SearchEntities' \
    '?pOrder=ENO&pPageNo={0}&pNoOfRecordsPerPage={1}&pStartEntryDate={2}' \
    '&pEndEntryDate={3}'

XML_API_URL_SITES_TOTAL_COUNT = 'http://dbforms.ga.gov.au/www/a.entities_api.get_total_number_records'
XML_API_URL_SITES_TOTAL_COUNT_DATE_RANGE = 'http://dbforms.ga.gov.au/www/a.entities_api.get_Number_Modified?' \
                                           'pModifiedFromDate={0}&pModifiedToDate={1}'


URI_NETWORK_CLASS = 'http://pid.geoscience.gov.au/def/ont/ga/pdm#SiteNetwork'
URI_NETWORK_INSTANCE_BASE = 'http://pid.geoscience.gov.au/network/'
URI_SITE_CLASS = 'http://pid.geoscience.gov.au/def/ont/ga/pdm#Site'
# URI_SITE_INSTANCE_BASE = 'http://localhost:5000/site/'
URI_SITE_INSTANCE_BASE = 'http://pid.geoscience.gov.au/site/ga/'

#
# surveys
#
XML_API_URL_SURVEY_REGISTER = 'http://dbforms.ga.gov.au/www/argus.argus_api.SearchSurveys' \
                              '?pOrder=SURVEYID&pPageno={0}&pNoOfRecordsPerPage={1}'
XML_API_URL_SURVEY = 'http://dbforms.ga.gov.au/www/argus.argus_api.survey?pSurveyNo={}'

BASE_URI_SURVEY = 'http://pid.geoscience.gov.au/survey/ga/'
URI_SURVEY_CLASS = 'http://pid.geoscience.gov.au/def/ont/ga/testing#Survey'

XML_API = {
    'ENTITIES': {
        'GET_CAPABILITIES': 'http://dbforms.ga.gov.au/www/a.entities_api.getCapabilities',
        'ENTITY': 'http://dbforms.ga.gov.au/www/a.entities_api.entities?pEno={}',
        'ENTITY_REGISTER': ''

    },
    'SURVEYS': {
        'GET_CAPABILITIES': 'http://dbforms.ga.gov.au/www/argus.argus_api.getCapabilities',
        'SURVEY': '',
        'SURVEY_REGISTER': 'http://dbforms.ga.gov.au/www/argus.argus_api.SearchSurveys'
                           '?pOrder=SURVEYID&pPageno={0}&pNoOfRecordsPerPage={1}'
    }
}