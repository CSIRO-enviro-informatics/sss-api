from pyldapi import Renderer, View
import requests
from flask import Response, render_template
from lxml import etree
from lxml import objectify
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from datetime import datetime
import json
json.encoder.FLOAT_REPR = lambda f: ("%.2f" % f)


class SiteRenderer(Renderer):
    URI_GA = 'http://pid.geoscience.gov.au/org/ga/geoscienceausralia'

    def __init__(self, request, xml=None):
        views = {
            "pdm": View(
                "GA's Public Data Model View",
                "Geoscience Australia's Public Data Model ontology",
                ["text/html", "text/turtle", "application/rdf+xml", "application/ld+json"],
                'text/html',
                profile_uri='http://pid.geoscience.gov.au/def/ont/ga/pdm'
            ),

            "nemsr": View(
                "The National Environmental Monitoring Sites Register View",
                "The National Environmental Monitoring Sites Register",
                ["application/vnd.geo+json"],
                "application/vnd.geo+json",
                profile_uri="http://www.neii.gov.au/nemsr"
            )
        }

        self.site_no = request.base_url.split('/')[-1]

        super(SiteRenderer, self).__init__(request, config.URI_SITE_INSTANCE_BASE + self.site_no, views, 'pdm')

        self.site_type = None
        self.description = None
        self.status = None
        self.entry_date = None
        self.geometry_type = None
        self.centroid_x = None
        self.centroid_y = None
        self.coords = None
        self.not_found = False

        if xml is not None:  # even if there are values for Oracle API URI and IGSN, load from XML file if present
            self._populate_from_xml_file(xml)
        else:
            self._populate_from_oracle_api()

    def validate_xml(self, xml):
        parser = etree.XMLParser(dtd_validation=False)

        try:
            etree.fromstring(xml, parser)
            return True
        except Exception:
            print('not valid xml')
            return False

    def _make_vocab_uri(self, xml_value, vocab_type):
        from model.lookups import TERM_LOOKUP
        if TERM_LOOKUP[vocab_type].get(xml_value) is not None:
            return TERM_LOOKUP[vocab_type].get(xml_value)
        else:
            return TERM_LOOKUP[vocab_type].get('unknown')

    def _make_vocab_alink(self, vocab_uri):
        if vocab_uri is not None:
            if vocab_uri.endswith('/'):
                return '<a href="{}">{}</a>'.format(vocab_uri, vocab_uri.split('/')[-2])
            else:
                return '<a href="{}">{}</a>'.format(vocab_uri, vocab_uri.split('/')[-1])

    def _generate_wkt(self):
        """
        Polygon: 8
        Point: 6889
        :return:
        :rtype:
        """
        if self.geometry_type == 'Point':
            coordinates = {
                'srid': 'GDA94',
                'x': self.x,
                'y': self.y
            }
            wkt = 'SRID={srid};POINT({x} {y})'.format(**coordinates)
        elif self.geometry_type == 'Polygon':
            start = 'SRID={srid};POLYGON(('.format(srid='GDA94')
            coordinates = ''
            for coord in zip(self.lons, self.lats):
                coordinates += '{} {},'.format(coord[0], coord[1])

            coordinates = coordinates[:-1]  # drop the final ','
            end = '))'
            wkt = '{start}{coordinates}{end}'.format(start=start, coordinates=coordinates, end=end)
        else:
            wkt = ''

        return wkt

    def _generate_google_map_js(self):
        if self.geometry_type == 'Point':
            js = '''
            var map = new google.maps.Map(document.getElementById("map"), {
                zoom: 6,
                center: myLatLng
            });

            var marker = new google.maps.Marker({
                position: myLatLng,
                map: map,
                title: 'Site %s'
            });
            ''' % self.site_no
        elif self.geometry_type == 'Polygon':
            coords = []
            for coord in zip(self.lons, self.lats):
                coords.append('\t\t\t\tnew google.maps.LatLng(%06.8f, %06.8f)' % (coord[1], coord[0]))
            # add the last first coordinate pair to end for complete polygon
            coords.append('\t\t\t\tnew google.maps.LatLng(%06.8f, %06.8f)' % (self.lats[0], self.lons[0]))
            js = '''
            var map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: myLatLng
            });

            var bboxCoords = new Array(
%s
            );
            // Construct the polygon.
            var bbox = new google.maps.Polygon({
                paths: bboxCoords,
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: '#FF0000',
                fillOpacity: 0.35
            });

            bbox.setMap(map);

            var bounds = new google.maps.LatLngBounds();        
            for (var i=0; i<bbox.getPath().length; i++) {                
                var point = new google.maps.LatLng(bboxCoords[i].lat(), bboxCoords[i].lng());
                bounds.extend(point);
            }            
            map.fitBounds(bounds);                           
            ''' % ',\n'.join(coords)
        else:
            js = ''

        return js

    def _populate_from_oracle_api(self):
        """
        Populates this instance with data from the Oracle Sites table API

        :param eno: (from class) the Entity Number of the Site desired
        :return: None
        """
        """
        Populates this instance with data from the Oracle Samples table API

        :param oracle_api_samples_url: the Oracle XML API URL string for a single sample
        :param igsn: the IGSN of the sample desired
        :return: None
        """
        # internal URI
        # os.environ['NO_PROXY'] = 'ga.gov.au'
        # call API
        r = requests.get(config.XML_API_URL_SITE.format(self.site_no))
        if "No data" in r.content.decode('utf-8'):
            self.not_found = True

        if self.validate_xml(r.content):
            self._populate_from_xml_file(r.content)
            return True
        else:
            return False

    def _populate_from_xml_file(self, xml):
        """
        Populates this instance with data from an XML file.

        :param xml: XML according to GA's Oracle XML API from the Samples DB
        :return: None
        """
        try:
            root = objectify.fromstring(xml)

            if hasattr(root.ROW, 'ENTITYID'):
                self.description = str(root.ROW.ENTITYID)
            if hasattr(root.ROW, 'ENTITY_TYPE'):
                self.site_type = self._make_vocab_uri(root.ROW.ENTITY_TYPE, 'site_type')
            if hasattr(root.ROW, 'GEOM'):
                # not using SDO_GTYP, 8001 & 8002 but instead checking for Point/Polygon etc by presense of child
                # element, e.g. SDO_POINT or SDO_ORDINATES
                if hasattr(root.ROW.GEOM, 'SDO_POINT'):
                    self.geometry_type = 'Point'
                    if hasattr(root.ROW.GEOM.SDO_POINT, 'X'):
                        self.x = float(root.ROW.GEOM.SDO_POINT.X)
                        self.centroid_x = self.x
                    else:
                        self.geometry_type = None  # i.e. without an x, this can't be a point. Likely a polygon
                    if hasattr(root.ROW.GEOM.SDO_POINT, 'Y'):
                        self.y = float(root.ROW.GEOM.SDO_POINT.Y)
                        self.centroid_y = self.y
                    if hasattr(root.ROW.GEOM.SDO_POINT, 'Z'):
                        self.z = float(root.ROW.GEOM.SDO_POINT.Z)

                if hasattr(root.ROW.GEOM, 'SDO_ORDINATES'):
                    self.geometry_type = 'Polygon'
                    self.lons = []
                    self.lats = []
                    self.coords = []
                    # iterate all children, splitting into lons & lats & ignoring elevs
                    for i, val in enumerate(root.ROW.GEOM.SDO_ORDINATES.getchildren()):
                        if i % 3 == 0:
                            self.lons.append(val)
                        elif (i - 1) % 3 == 0:
                            self.lats.append(val)
                    self.centroid_x = sum(self.lons) / len(self.lons)
                    self.centroid_y = sum(self.lats) / len(self.lats)
            if hasattr(root.ROW, 'ACCESS_CODE'):
                self.access_code = root.ROW.ACCESS_CODE
            if hasattr(root.ROW, 'ENTRYDATE'):
                self.entry_date = str(root.ROW.ENTRYDATE).split('T')[0]
            if hasattr(root.ROW, 'COUNTRY'):
                self.country = root.ROW.COUNTRY

        except Exception as e:
            print(e)

        return True

    def render(self):
        if self.not_found:
            return Response('Sample {} not found.'.format(self.site_no), status=404, mimetype='text/plain')

        response = super().render()  # alternates and all view
        if response is None:
            if self.view == 'pdm':
                if self.format == 'text/html':
                    return self.export_html(model_view=self.view)
                else:
                    return Response(self.export_rdf(self.view, self.format), mimetype=self.format, headers=self.headers)
            elif self.view == 'nemsr':
                return self.export_nemsr_geojson()
        else:
            return response

    def _render_alternates_view_html(self):
        return Response(
            render_template(
                self.alternates_template or 'alternates.html',
                instance_uri=config.URI_SITE_CLASS,
                register_name='Site Register',
                class_uri=self.site_type,
                default_view_token=self.default_view_token,
                views=self.views
            ),
            headers=self.headers
        )

    def _make_geojson_geometry(self):
        if self.geometry_type == 'Point':
            g = {
                'type': 'Point',
                'coordinates': [
                    self.x, self.y, self.z
                ]
            }
        else:  # elif self.geometry_type == 'Polygon':
            coords = []
            for coord in zip(self.lons, self.lats):
                coords.append([float(coord[0]), float(coord[1])])
            g = {
                'type': 'Polygon',
                'coordinates': [
                    coords
                ]
            }

        return g

    def export_nemsr_geojson(self):
        """
        NEII documentation for site GeoJSON properties: http://www.neii.gov.au/nemsr/documentation/1.0/data-fields/site
        :return:
        :rtype:
        """
        site = {
            'type': 'FeatureCollection',
            'properties': {
                'network': {}  # TODO: generate this in network.py and import
            },
            'features': {
                'type': 'Feature',
                'id': '{}{}'.format(config.URI_SITE_INSTANCE_BASE, self.site_no),
                'geometry': self._make_geojson_geometry(),
                'crs': {
                    'type': 'link',
                    'properties': {
                        'href': 'http://www.opengis.net/def/crs/EPSG/0/4283',
                    # the NEII examples use WGS-84, we GDA-94
                        'type': 'proj4'  # TODO: Irina to check this
                    }
                },
                'properties': {
                    'name': '{} {}'.format('Site', self.site_no),
                    'siteDescription': self.description,
                    'siteLicence': 'open-CC',  # http://cloud.neii.gov.au/neii/neii-licencing/version-1/concept
                    'siteURL': '{}{}'.format(config.URI_SITE_INSTANCE_BASE, self.site_no),
                    'operatingAuthority': {
                        'name': 'Geoscience Australia',
                        'id': self.URI_GA
                    }
                },
                'siteStatus': self.status,
                'extensionFieldValue1': '',  # TODO: find our obligations for this and other extension values
                'extensionFieldValue2': '',
                'extensionFieldValue3': '',
                'extensionFieldValue4': '',
                'extensionFieldValue5': '',
                'observingCapabilities': {}  # TODO: generate this in observing_capabilities.py and import
            },
        }
        return Response(
            json.dumps(site),
            mimetype='application/vnd.geo+json',
            headers=self.headers
        )

    def export_rdf(self, model_view='pdm', rdf_mime='text/turtle'):
        """
        Exports this instance in RDF, according to a given model from the list of supported models,
        in a given rdflib RDF format

        :param model_view: string of one of the model view names available for Sample objects ['igsn', 'dc', '',
            'default']
        :param rdf_mime: string of one of the rdflib serlialization format ['n3', 'nquads', 'nt', 'pretty-xml', 'trig',
            'trix', 'turtle', 'xml'], from http://rdflib3.readthedocs.io/en/latest/plugin_serializers.html
        :return: RDF string
        """

        '''
        <http://pid.geoscience.gov.au/site/9810> a <http://vocabulary.odm2.org/samplingfeaturetype/borehole>, <http://www.w3.org/2002/07/owl#NamedIndividual> ;
            samfl:samplingElevation [ a samfl:Elevation ;
            samfl:elevation "231.69716"^^xsd:float ;
            samfl:verticalDatum "http://spatialreference.org/ref/epsg/4283/"^^xsd:anyUri ] ;
            geosp:hasGeometry [ 
                a geosp:Geometry ;
                geosp:asWKT "SRID=GDA94;POINT(143.36786389 -25.94903611)"^^geosp:wktLiteral 
            ] .

        <http://registry.it.csiro.au/sandbox/csiro/oznome/feature/earth-realm/lithosphere> a sosa:FeatureOfInterest ;
            skos:exactMatch <http://sweetontology.net/realmGeol/Lithosphere> .

        <http://vocabulary.odm2.org/samplingfeaturetype/borehole> rdfs:subClassOf sosa:Sample .
        '''
        # things that are applicable to all model views; the graph and some namespaces
        g = Graph()
        GEO = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', GEO)

        # URI for this site
        this_site = URIRef(config.URI_SITE_INSTANCE_BASE + self.site_no)
        g.add((this_site, RDF.type, URIRef(self.site_type)))
        g.add((this_site, RDF.type, URIRef('http://www.w3.org/2002/07/owl#NamedIndividual')))
        g.add((this_site, RDFS.label, Literal('Site ' + self.site_no, datatype=XSD.string)))
        g.add((this_site, RDFS.comment, Literal(self.description, datatype=XSD.string)))
        site_geometry = BNode()
        g.add((this_site, GEO.hasGeometry, site_geometry))
        g.add((site_geometry, RDF.type, GEO.Geometry))
        g.add((site_geometry, GEO.asWKT, Literal(self._generate_wkt(), datatype=GEO.wktLiteral)))

        return g.serialize(format=self._get_rdf_mimetype(rdf_mime))

    def _get_rdf_mimetype(self, rdf_mime):
        return self.RDF_SERIALIZER_MAP[rdf_mime]

    def export_html(self, model_view='pdm'):
        """
        Exports this instance in HTML, according to a given model from the list of supported models.

        :param model_view: string of one of the model view names available for Sample objects ['igsn', 'dc', '',
            'default']
        :return: HTML string
        """
        if model_view == 'pdm':
            view_title = 'PDM Ontology view'
            sample_table_html = render_template(
                'class_site_pdm.html',
                site_no=self.site_no,
                description=self.description,
                wkt=self._generate_wkt(),
                state=None,  # TODO: calculate
                site_type_alink=self._make_vocab_alink(self.site_type),
                entry_date=self.entry_date
            )
        elif model_view == 'prov':
            view_title = 'PROV Ontology view'
            prov_turtle = self.export_rdf('prov', 'text/turtle')
            g = Graph().parse(data=prov_turtle, format='turtle')

            sample_table_html = render_template(
                'class_site_prov.html',
                visjs=self._make_vsjs(g),
                prov_turtle=prov_turtle,
            )
        else:  # elif model_view == 'dc':
            view_title = 'Dublin Core view'

            sample_table_html = render_template(
                'class_site_dc.html',
                identifier=self.site_no,
                description=self.description,
                date=self.entry_date,
                type=self.site_type,
                wkt=self._generate_wkt(),
                creator='<a href="{}">Geoscience Australia</a>'.format(self.URI_GA),
                publisher='<a href="{}">Geoscience Australia</a>'.format(self.URI_GA),
            )

        # add in the Pingback header links as they are valid for all HTML views
        pingback_uri = config.URI_SITE_INSTANCE_BASE + self.site_no + "/pingback"
        self.headers['Link'] += ', <{}>; rel="http://www.w3.org/ns/prov#pingback"'.format(pingback_uri)

        return Response(
            render_template(
                'page_site.html',
                view=model_view,
                site_no=self.site_no,
                entry_date=self.entry_date,
                view_title=view_title,
                sample_table_html=sample_table_html,
                date_now=datetime.now().strftime('%d %B %Y'),
                gm_key=config.GOOGLE_MAPS_API_KEY,
                google_maps_js=self._generate_google_map_js(),
                lat=self.centroid_y,
                lon=self.centroid_x,
                geometry_type=self.geometry_type,
                coords=self.coords,
                base_url=config.BASE_URL
            ),
            headers=self.headers
        )


class ParameterError(ValueError):
    pass


if __name__ == '__main__':
    # s = Site(17943)
    # s._populate_from_oracle_api()
    # print(s.export_nemsr_geojson())
    pass
