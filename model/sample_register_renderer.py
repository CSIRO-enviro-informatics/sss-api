from pyldapi import RegisterRenderer
from flask import render_template
from io import StringIO, BytesIO
from lxml import etree
import requests
import _config as conf


class SampleRegisterRenderer(RegisterRenderer):
    def __init__(self, request, uri, label, comment, register_items, contained_item_classes, register_total_count,
                 base_uri
                 ):
        super(SampleRegisterRenderer, self).__init__(request, uri, label, comment, register_items, contained_item_classes, register_total_count)

        self.base_uri = base_uri
        self.register = []

        self._get_details_from_oracle_api(self.page, self.per_page)

    def render(self):
        # print(self.contained_item_classes)
        return render_template(
            self.register_template or 'register.html',
            organisation_branding='ga',
            class_name=self.uri,
            register=self.register,
            uri=self.uri,
            label=self.label,
            contained_item_classes=self.contained_item_classes,
            register_items=self.register_items,
            page=self.page,
            per_page=self.per_page,
            first_page=self.first_page,
            prev_page=self.prev_page,
            next_page=self.next_page,
            last_page=self.last_page,
            super_register=self.super_register,
        )

    def _get_details_from_file(self, file_path=None, xml_content=None):
        """
        Populates this instance with data from an XML file.

        :param xml: XML according to GA's Oracle XML API from the Samples DB
        :return: None
        """
        if file_path is not None:
            xml = open(file_path, 'rb')
        elif xml_content is not None:
            xml = BytesIO(xml_content)
        else:
            raise ValueError('You must specify either a file path or file XML contents')

        for event, elem in etree.iterparse(xml):
            if elem.tag == "IGSN":
                self.register.append(elem.text)

    def _get_details_from_oracle_api(self, page, per_page):
        """
        Populates this instance with data from the Oracle Samples table API

        :param page: the page number of the total resultset from the Samples Set API
        :return: None
        """
        #os.environ['NO_PROXY'] = 'ga.gov.au'
        r = requests.get(conf.XML_API_URL_SAMPLESET.format(page, per_page), timeout=3)
        xml = r.content

        if self.validate_xml(xml):
            self._get_details_from_file(xml_content=xml)
            return True
        else:
            return False

    def validate_xml(self, xml):
        parser = etree.XMLParser(dtd_validation=False)

        try:
            etree.fromstring(xml, parser)
            return True
        except Exception:
            print('not valid xml')
            return False