from pyldapi import Renderer, View
from lxml import etree
from lxml import objectify
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal, BNode
import requests
from datetime import datetime
from flask import Response, render_template, redirect
import _config as config


class SurveyRenderer(Renderer):
    """
        This class represents a Survey and methods in this class allow one to be loaded from GA's internal Oracle
        ARGUS database and to be exported in a number of mimetypes including RDF, according to the 'GA Public Data Ontology'
        and PROV-O, the Provenance Ontology.
    """

    URI_MISSSING = 'http://www.opengis.net/def/nil/OGC/0/missing'
    URI_INAPPLICABLE = 'http://www.opengis.net/def/nil/OGC/0/inapplicable'
    URI_GA = 'http://pid.geoscience.gov.au/org/ga'

    def __init__(self, request, xml=None):
        views = {
            "gapd": View(
                'GA Public Data View',
                "Geoscience Australia's Public Data Model",
                ['text/html', 'text/turtle', 'application/rdf+xml', 'application/rdf+json', 'application/json'],
                'text/html',
                namespace=None
            ),

            "argus": View(
                'The Airborne Reductions Group Utility System View',
                "Geoscience Australia's Airborne Reductions Group Utility System (ARGUS)",
                ["text/xml"],
                'text/xml',
                namespace=None
            ),

            'sosa': View(
                'SOSA View',
                "The W3C's Sensor, Observation, Sample, and Actuator ontology within the Semantic Sensor Networks ontology",
                ["text/turtle", "application/rdf+xml", "application/rdf+json"],
                "text/turtle",
                namespace="http://www.w3.org/ns/sosa/"
            ),

            'prov': View(
                'PROV View',
                "The W3C's provenance data model, PROV",
                ["text/html", "text/turtle", "application/rdf+xml", "application/rdf+json"],
                "text/turtle",
                namespace="http://www.w3.org/ns/prov/"
            )
        }

        self.survey_no = request.base_url.split('/')[-1]
        
        super(SurveyRenderer, self).__init__(request, config.URI_SURVEY_INSTANCE_BASE + self.survey_no, views, "gapd")

        self.survey_name = None
        self.state = None
        self.operator = None
        self.contractor = None
        self.processor = None
        self.survey_type = None
        self.data_types = None
        self.vessel = None
        self.vessel_type = None
        self.release_date = None
        self.onshore_offshore = None
        self.start_date = None
        self.end_date = None
        self.w_long = None
        self.e_long = None
        self.s_lat = None
        self.n_lat = None
        self.line_km = None
        self.total_km = None
        self.line_spacing = None
        self.line_direction = None
        self.tie_spacing = None
        self.square_km = None
        self.crystal_volume = None
        self.up_crystal_volume = None
        self.digital_data = None
        self.geodetic_datum = None
        self.asl = None
        self.agl = None
        self.mag_instrument = None
        self.rad_instrument = None

        self.srid = 8311  # TODO: replace this magic number with a value from the DB

        # populate all instance variables from API
        # TODO: lazy load this, i.e. only populate if a controller that need populating is loaded which is every controller except for Alternates
        if xml is not None:  # even if there are values for Oracle API URI and IGSN, load from XML file if present
            self._populate_from_xml_file(xml)
        else:
            self._populate_from_oracle_api()

        # these coordinate things can only be calculated after populating variables from XML file / XML API
        self.wkt_polygon = self._generate_wkt()

        self.centroid_lat = (self.n_lat + self.s_lat) / 2
        self.centroid_lon = (self.e_long + self.w_long) / 2

        # clean-up required vars
        if self.end_date is None:
            self.end_date = datetime(1900, 1, 1)

    def render(self):
        if self.survey_name is None:
            return Response('Survey with ID {} not found.'.format(self.survey_no), status=404, mimetype='text/plain')
        if self.view == "alternates":
            return self._render_alternates_view()
        elif self.view == 'gapd':
            if self.format == 'text/html':
                return self.export_html(model_view=self.view)
            else:
                return Response(self.export_rdf(self.view, self.format), mimetype=self.format)
        elif self.view == 'argus':  # XML only for this controller
            return redirect(config.XML_API_URL_SURVEY.format(self.survey_no), code=303)
        elif self.view == 'prov':
            if self.format == 'text/html':
                return self.export_html(model_view=self.view)
            else:
                return Response(self.export_rdf(self.view, self.format), mimetype=self.format)
        elif self.view == 'sosa':  # RDF only for this controller
            return Response(self.export_rdf(self.view, self.format), mimetype=self.format)

    def _render_alternates_view_html(self):
        return Response(
            render_template(
                self.alternates_template or 'alternates.html',
                register_name='Survey Register',
                class_uri=self.uri,
                instance_uri=config.BASE_URI_SURVEY + self.survey_no,
                default_view_token=self.default_view_token,
                views=self.views
            ),
            headers=self.headers
        )

    def validate_xml(self, xml):
        parser = etree.XMLParser(dtd_validation=False)

        try:
            etree.fromstring(xml, parser)
            return True
        except Exception:
            print('not valid xml')
            return False

    def _populate_from_oracle_api(self):
        """
        Populates this instance with data from the Oracle ARGUS table API
        """
        # internal URI
        # os.environ['NO_PROXY'] = 'ga.gov.au'
        # call API
        r = requests.get(config.XML_API_URL_SURVEY.format(self.survey_no))
        # deal with missing XML declaration
        if "No data" in r.text:
            raise ParameterError('No Data')

        xml = r.text

        if self.validate_xml(xml):
            self._populate_from_xml_file(xml)
            return True
        else:
            return False

    def _populate_from_xml_file(self, xml):
        """
        Populates this instance with data from an XML file.

        :param xml: XML according to GA's Oracle XML API from the Samples DB
        :return: None
        """
        '''
        example from API: http://www.ga.gov.au/www/argus.argus_api.survey?pSurveyNo=921

        <?xml version="1.0" ?>
        <ROWSET>
            <ROW>
                <SURVEYID>921</SURVEYID>
                <SURVEYNAME>Goomalling, WA, 1996</SURVEYNAME>
                <STATE>WA</STATE>
                <OPERATOR>Stockdale Prospecting Ltd.</OPERATOR>
                <CONTRACTOR>Kevron Geophysics Pty Ltd</CONTRACTOR>
                <PROCESSOR>Kevron Geophysics Pty Ltd</PROCESSOR>
                <SURVEY_TYPE>Detailed</SURVEY_TYPE>
                <DATATYPES>MAG,RAL,ELE</DATATYPES>
                <VESSEL>Aero Commander</VESSEL>
                <VESSEL_TYPE>Plane</VESSEL_TYPE>
                <RELEASEDATE/>
                <ONSHORE_OFFSHORE>Onshore</ONSHORE_OFFSHORE>
                <STARTDATE>05-DEC-96</STARTDATE>
                <ENDDATE>22-DEC-96</ENDDATE>
                <WLONG>116.366662</WLONG>
                <ELONG>117.749996</ELONG>
                <SLAT>-31.483336</SLAT>
                <NLAT>-30.566668</NLAT>
                <LINE_KM>35665</LINE_KM>
                <TOTAL_KM/>
                <LINE_SPACING>250</LINE_SPACING>
                <LINE_DIRECTION>180</LINE_DIRECTION>
                <TIE_SPACING/>
                <SQUARE_KM/>
                <CRYSTAL_VOLUME>33.6</CRYSTAL_VOLUME>
                <UP_CRYSTAL_VOLUME>4.2</UP_CRYSTAL_VOLUME>
                <DIGITAL_DATA>MAG,RAL,ELE</DIGITAL_DATA>
                <GEODETIC_DATUM>WGS84</GEODETIC_DATUM>
                <ASL/>
                <AGL>60</AGL>
                <MAG_INSTRUMENT>Scintrex CS2</MAG_INSTRUMENT>
                <RAD_INSTRUMENT>Exploranium GR820</RAD_INSTRUMENT>
            </ROW>
        </ROWSET>
        '''
        # turn the XML doc into a Python object
        root = objectify.fromstring(xml)

        if hasattr(root.ROW, 'SURVEYNAME'):
            self.survey_name = root.ROW.SURVEYNAME
        if hasattr(root.ROW, 'STATE'):
            self.state = root.ROW.STATE
        if hasattr(root.ROW, 'OPERATOR'):
            self.operator = root.ROW.OPERATOR
        if hasattr(root.ROW, 'CONTRACTOR'):
            self.contractor = root.ROW.CONTRACTOR
        if hasattr(root.ROW, 'PROCESSOR'):
            self.processor = root.ROW.PROCESSOR
        if hasattr(root.ROW, 'SURVEY_TYPE'):
            self.survey_type = root.ROW.SURVEY_TYPE
        if hasattr(root.ROW, 'DATATYPES'):
            self.data_types = root.ROW.DATATYPES
        if hasattr(root.ROW, 'VESSEL'):
            self.vessel = root.ROW.VESSEL
        if hasattr(root.ROW, 'VESSEL_TYPE'):
            self.vessel_type = root.ROW.VESSEL_TYPE
        if hasattr(root.ROW, 'RELEASEDATE'):
            self.release_date = datetime.strptime(root.ROW.RELEASEDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.RELEASEDATE.text is not None else None
        if hasattr(root.ROW, 'ONSHORE_OFFSHORE'):
            self.onshore_offshore = root.ROW.ONSHORE_OFFSHORE
        if hasattr(root.ROW, 'STARTDATE'):
            self.start_date = datetime.strptime(root.ROW.STARTDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.STARTDATE.text is not None else None
        if hasattr(root.ROW, 'ENDDATE'):
            self.end_date = datetime.strptime(root.ROW.ENDDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.ENDDATE.text is not None else None
        if hasattr(root.ROW, 'WLONG'):
            self.w_long = root.ROW.WLONG
        if hasattr(root.ROW, 'ELONG'):
            self.e_long = root.ROW.ELONG
        if hasattr(root.ROW, 'SLAT'):
            self.s_lat = root.ROW.SLAT
        if hasattr(root.ROW, 'NLAT'):
            self.n_lat = root.ROW.NLAT
        if hasattr(root.ROW, 'LINE_KM'):
            self.line_km = root.ROW.LINE_KM
        if hasattr(root.ROW, 'TOTAL_KM'):
            self.total_km = root.ROW.TOTAL_KM
        if hasattr(root.ROW, 'LINE_SPACING'):
            self.line_spacing = root.ROW.LINE_SPACING
        if hasattr(root.ROW, 'LINE_DIRECTION'):
            self.line_direction = root.ROW.LINE_DIRECTION
        if hasattr(root.ROW, 'TIE_SPACING'):
            self.tie_spacing = root.ROW.TIE_SPACING
        if hasattr(root.ROW, 'SQUARE_KM'):
            self.square_km = root.ROW.SQUARE_KM
        if hasattr(root.ROW, 'CRYSTAL_VOLUME'):
            self.crystal_volume = root.ROW.CRYSTAL_VOLUME
        if hasattr(root.ROW, 'UP_CRYSTAL_VOLUME'):
            self.up_crystal_volume = root.ROW.UP_CRYSTAL_VOLUME
        if hasattr(root.ROW, 'DIGITAL_DATA'):
            self.digital_data = root.ROW.DIGITAL_DATA
        if hasattr(root.ROW, 'GEODETIC_DATUM'):
            self.geodetic_datum = root.ROW.GEODETIC_DATUM
        if hasattr(root.ROW, 'ASL'):
            self.asl = root.ROW.ASL
        if hasattr(root.ROW, 'AGL'):
            self.agl = root.ROW.AGL
        if hasattr(root.ROW, 'MAG_INSTRUMENT'):
            self.mag_instrument = root.ROW.MAG_INSTRUMENT
        if hasattr(root.ROW, 'RAD_INSTRUMENT'):
            self.rad_instrument = root.ROW.RAD_INSTRUMENT

    # def _generate_survey_gml(self):
    #     if self.z is not None:
    #         gml = '<gml:Point srsDimension="3" srsName="https://epsg.io/' + self.srid + '">' \
    #               '<gml:pos>' + self.x + ' ' + self.y + ' ' + self.z + '</gml:pos>' \
    #               '</gml:Point>'
    #     else:
    #         if self.srid is not None and self.x is not None and self.y is not None:
    #             gml = '<gml:Point srsDimension="2" srsName="https://epsg.io/' + self.srid + '">' \
    #                   '<gml:pos>' + self.x + ' ' + self.y + '</gml:pos>' \
    #                   '</gml:Point>'
    #         else:
    #             gml = ''
    #
    #     return gml

    def _generate_wkt(self):
        return 'SRID={};POLYGON(({} {}, {} {}, {} {}, {} {}, {} {}))'.format(
            self.srid,
            self.w_long, self.n_lat,
            self.e_long, self.n_lat,
            self.e_long, self.s_lat,
            self.e_long, self.s_lat,
            self.w_long, self.n_lat
        )

    def export_rdf(self, model_view='default', rdf_mime='text/turtle'):
        """
        Exports this instance in RDF, according to a given model from the list of supported models,
        in a given rdflib RDF mimetype

        :param model_view: string of one of the model controller names available for Sample objects ['igsn', 'dc', '',
            'default']
        :param rdf_mime: string of one of the rdflib serlialization mimetype ['n3', 'nquads', 'nt', 'pretty-xml', 'trig',
            'trix', 'turtle', 'xml'], from http://rdflib3.readthedocs.io/en/latest/plugin_serializers.html
        :return: RDF string
        """

        # things that are applicable to all model views; the graph and some namespaces
        g = Graph()

        # URI for this survey
        this_survey = URIRef(config.URI_SURVEY_INSTANCE_BASE + self.survey_no)

        # define GA
        ga = URIRef(SurveyRenderer.URI_GA)

        # select model controller
        if model_view == 'gapd' or model_view == 'prov':
            PROV = Namespace('http://www.w3.org/ns/prov#')
            g.bind('prov', PROV)

            g.add((this_survey, RDF.type, PROV.Activity))

            GEOSP = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geosp', GEOSP)

            AUROLE = Namespace('http://communications.data.gov.au/def/role/')
            g.bind('aurole', AUROLE)

            # default model is the GAPD model
            # Activity properties
            # TODO: add in label, startedAtTime, endedAtTime, atLocation

            # Agents
            contractor = BNode()
            contractor_agent = BNode()
            g.add((contractor_agent, RDF.type, PROV.Agent))
            g.add((contractor, RDF.type, PROV.Attribution))
            g.add((contractor, PROV.agent, contractor_agent))
            g.add((contractor, PROV.hadRole, AUROLE.PrincipalInvestigator))
            g.add((contractor_agent, RDFS.label, Literal(self.contractor, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, contractor))

            operator = BNode()
            operator_agent = BNode()
            g.add((operator_agent, RDF.type, PROV.Agent))
            g.add((operator, RDF.type, PROV.Attribution))
            g.add((operator, PROV.agent, operator_agent))
            g.add((operator, PROV.hadRole, AUROLE.Sponsor))
            g.add((operator_agent, RDFS.label, Literal(self.operator, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, operator))

            processor = BNode()
            processor_agent = BNode()
            g.add((processor_agent, RDF.type, PROV.Agent))
            g.add((processor, RDF.type, PROV.Attribution))
            g.add((processor, PROV.agent, processor_agent))
            g.add((processor, PROV.hadRole, AUROLE.Processor))
            g.add((processor_agent, RDFS.label, Literal(self.processor, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, processor))

            publisher = BNode()
            g.add((ga, RDF.type, PROV.Org))
            g.add((publisher, RDF.type, PROV.Attribution))
            g.add((publisher, PROV.agent, ga))
            g.add((publisher, PROV.hadRole, AUROLE.Publisher))
            g.add((ga, RDFS.label, Literal("Geoscience Australia", datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, publisher))

            # TODO: add in other Agents

            if model_view == 'gapd':
                # Geometry
                SAMFL = Namespace('http://def.seegrid.csiro.au/ontology/om/sam-lite#')
                g.bind('samfl', SAMFL)

                # Survey location in GML & WKT, formulation from GeoSPARQL

                geometry = BNode()
                g.add((this_survey, PROV.hadLocation, geometry))
                g.add((geometry, RDF.type, SAMFL.Polygon))
                # g.add((geometry, GEOSP.asGML, gml))
                g.add((geometry, GEOSP.asWKT, Literal(self._generate_wkt(), datatype=GEOSP.wktLiteral)))

                # GAPD model required namespaces
                GAPD = Namespace('http://pid.geoscience.gov.au/def/ont/gapd#')
                g.bind('gapd', GAPD)

                # classing the Survey in GAPD
                g.add((this_survey, RDF.type, GAPD.PublicSurvey))

                # TODO: add in other Survey properties
            elif model_view == 'prov':
                # redundant relationships just for SVG viewing
                # TODO: add in a recognition of Agent roles for the graph
                g.add((this_survey, RDFS.label, Literal('Survey ' + self.survey_no, datatype=XSD.string)))
                g.add((ga, RDF.type, PROV.Agent))
                g.add((this_survey, PROV.wasAssociatedWith, contractor_agent))
                g.add((this_survey, PROV.wasAssociatedWith, operator_agent))
                g.add((this_survey, PROV.wasAssociatedWith, processor_agent))
                g.add((this_survey, PROV.wasAssociatedWith, ga))
        elif model_view == 'sosa':
            SOSA = Namespace('http://www.w3.org/ns/sosa/')
            g.bind('sosa', SOSA)

            # Sampling
            g.add((this_survey, RDF.type, SOSA.Sampling))
            TIME = Namespace('http://www.w3.org/2006/time#')
            g.bind('time', TIME)

            if self.start_date is not None and self.end_date is not None:
                t = BNode()
                g.add((t, RDF.type, TIME.ProperInterval))

                start = BNode()
                g.add((start, RDF.type, TIME.Instant))
                g.add((start, TIME.inXSDDateTime, Literal(self.start_date.date(), datatype=XSD.date)))
                g.add((t, TIME.hasBeginning, start))
                finish = BNode()
                g.add((finish, RDF.type, TIME.Instant))
                g.add((finish, TIME.inXSDDateTime, Literal(self.end_date.date(), datatype=XSD.date)))
                g.add((t, TIME.hasEnd, finish))
                g.add((this_survey, TIME.hasTime, t))  # associate

            elif self.start_date is not None:
                t = BNode()
                g.add((t, RDF.type, TIME.Instant))
                g.add((t, TIME.inXSDDateTime, Literal(self.start_date.date(), datatype=XSD.date)))
                g.add((this_survey, TIME.hasTime, t))  # associate

            # Platform  # TODO: add lookup for 'Plane' etc to a vessel type vocab
            platform = BNode()
            g.add((platform, RDF.type, URIRef('http://pid.geoscience.gov.au/platform/' + self.vessel_type)))
            g.add((platform, RDFS.subClassOf, SOSA.Platform))
            g.add((platform, RDFS.label, Literal(self.vessel, datatype=XSD.string)))

            # Sampler
            if self.mag_instrument is not None:
                sampler_mag = BNode()
                g.add((sampler_mag, RDF.type, URIRef(self.mag_instrument)))
                g.add((sampler_mag, RDFS.subClassOf, SOSA.Sampler))
                g.add((sampler_mag, SOSA.madeSampling, this_survey))  # associate # TODO: resolve double madeSampling
                g.add((sampler_mag, SOSA.isHostedBy, platform))  # associate

            if self.rad_instrument is not None:
                sampler_rad = BNode()
                g.add((sampler_rad, RDF.type, URIRef(self.rad_instrument)))
                g.add((sampler_rad, RDFS.subClassOf, SOSA.Sampler))
                g.add((sampler_rad, SOSA.madeSampling, this_survey))  # associate
                g.add((sampler_rad, SOSA.isHostedBy, platform))  # associate

            if self.mag_instrument is None and self.rad_instrument is None:
                sampler = BNode()
                g.add((sampler, RDF.type, SOSA.Sampler))
                g.add((sampler, SOSA.isHostedBy, platform))  # associate

            # FOI
            foi = URIRef('http://pid.geoscience.gov.au/feature/earthSusbsurface')
            g.add((foi, RDFS.label, Literal('Earth Subsurface', datatype=XSD.string)))
            g.add((foi, RDFS.comment, Literal('Below the earth\'s terrestrial surface', datatype=XSD.string)))
            g.add((this_survey, SOSA.hasFeatureOfInterest, foi))  # associate

            # Sample
            sample = BNode()
            g.add((sample, RDF.type, SOSA.Sample))
            g.add((this_survey, SOSA.hasResult, sample))  # associate
            g.add((foi, SOSA.hasSample, sample))  # associate with FOI

            # Sample geometry
            GEOSP = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geosp', GEOSP)
            geometry = BNode()
            g.add((geometry, RDF.type, GEOSP.Geometry))
            g.add((geometry, GEOSP.asWKT, Literal(self._generate_wkt(), datatype=GEOSP.wktLiteral)))
            g.add((sample, GEOSP.hasGeometry, geometry))  # associate

        return g.serialize(format=self._get_rdf_mimetype(rdf_mime))

    def _get_rdf_mimetype(self, rdf_mime):
        return self.RDF_SERIALIZER_MAP[rdf_mime]

    # TODO: split these RDF --> SVG parts into a stand-alone module
    def __graph_preconstruct(self, g):
        u = '''
            PREFIX prov: <http://www.w3.org/ns/prov#>
            DELETE {
                ?a prov:generated ?e .
            }
            INSERT {
                ?e prov:wasGeneratedBy ?a .
            }
            WHERE {
                ?a prov:generated ?e .
            }
        '''
        g.update(u)

        return g

    def __gen_visjs_nodes(self, g):
        nodes = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s a ?o .
                {?s a prov:Entity .}
                UNION
                {?s a prov:Activity .}
                UNION
                {?s a prov:Agent .}
                OPTIONAL {?s rdfs:label ?label .}
            }
            '''
        for row in g.query(q):
            if str(row['o']) == 'http://www.w3.org/ns/prov#Entity':
                if row['label'] is not None:
                    label = row['label']
                else:
                    label = 'Entity'
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", shape: "ellipse", color:{background:"#FFFC87", border:"#808080"}},\n' % {
                    'node_id': row['s'],
                    'label': label
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Activity':
                if row['label'] is not None:
                    label = row['label']
                else:
                    label = 'Activity'
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", shape: "box", color:{background:"#9FB1FC", border:"blue"}},\n' % {
                    'node_id': row['s'],
                    'label': label
                }
            elif str(row['o']) == 'http://www.w3.org/ns/prov#Agent':
                if row['label'] is not None:
                    label = row['label']
                else:
                    label = 'Agent'
                nodes += '\t\t\t\t{id: "%(node_id)s", label: "%(label)s", image: "/surveys/static/img/agent.png", shape: "image"},\n' % {
                    'node_id': row['s'],
                    'label': label
                }

        return nodes

    def __gen_visjs_edges(self, g):
        edges = ''

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT *
            WHERE {
                ?s ?p ?o .
                ?s prov:wasAttributedTo|prov:wasGeneratedBy|prov:used|prov:wasDerivedFrom|prov:wasInformedBy|prov:wasAssociatedWith ?o .
            }
            '''
        for row in g.query(q):
            edges += '\t\t\t\t{from: "%(from)s", to: "%(to)s", arrows:"to", font: {align: "bottom"}, color:{color:"black"}, label: "%(relationship)s"},\n' % {
                'from': row['s'],
                'to': row['o'],
                'relationship': str(row['p']).split('#')[1]
            }

        return edges

    def _make_vsjs(self, g):
        g = self.__graph_preconstruct(g)

        nodes = 'var nodes = new vis.DataSet([\n'
        nodes += self.__gen_visjs_nodes(g)
        nodes = nodes.rstrip().rstrip(',') + '\n\t\t\t]);\n'

        edges = 'var edges = new vis.DataSet([\n'
        edges += self.__gen_visjs_edges(g)
        edges = edges.rstrip().rstrip(',') + '\n\t\t\t]);\n'

        visjs = '''
        %(nodes)s

        %(edges)s

        var container = document.getElementById('network');

        var data = {
            nodes: nodes,
            edges: edges,
        };

        var options = {};
        var network = new vis.Network(container, data, options);
        ''' % {'nodes': nodes, 'edges': edges}

        return visjs

    def export_html(self, model_view='gapd'):
        """
        Exports this instance in HTML, according to a given model from the list of supported models.

        :param model_view: string of one of the model controller names available for survey objects
        :return: HTML string
        """
        '''
        <?xml version="1.0" ?>
        <ROWSET>
         <ROW>
          <SURVEYID>921</SURVEYID>
          <SURVEYNAME>Goomalling, WA, 1996</SURVEYNAME>
          <STATE>WA</STATE>
          <OPERATOR>Stockdale Prospecting Ltd.</OPERATOR>
          <CONTRACTOR>Kevron Geophysics Pty Ltd</CONTRACTOR>
          <PROCESSOR>Kevron Geophysics Pty Ltd</PROCESSOR>
          <SURVEY_TYPE>Detailed</SURVEY_TYPE>
          <DATATYPES>MAG,RAL,ELE</DATATYPES>
          <VESSEL>Aero Commander</VESSEL>
          <VESSEL_TYPE>Plane</VESSEL_TYPE>
          <RELEASEDATE/>
          <ONSHORE_OFFSHORE>Onshore</ONSHORE_OFFSHORE>
          <STARTDATE>05-DEC-96</STARTDATE>
          <ENDDATE>22-DEC-96</ENDDATE>
          <WLONG>116.366662</WLONG>
          <ELONG>117.749996</ELONG>
          <SLAT>-31.483336</SLAT>
          <NLAT>-30.566668</NLAT>
          <LINE_KM>35665</LINE_KM>
          <TOTAL_KM/>
          <LINE_SPACING>250</LINE_SPACING>
          <LINE_DIRECTION>180</LINE_DIRECTION>
          <TIE_SPACING/>
          <SQUARE_KM/>
          <CRYSTAL_VOLUME>33.6</CRYSTAL_VOLUME>
          <UP_CRYSTAL_VOLUME>4.2</UP_CRYSTAL_VOLUME>
          <DIGITAL_DATA>MAG,RAL,ELE</DIGITAL_DATA>
          <GEODETIC_DATUM>WGS84</GEODETIC_DATUM>
          <ASL/>
          <AGL>60</AGL>
          <MAG_INSTRUMENT>Scintrex CS2</MAG_INSTRUMENT>
          <RAD_INSTRUMENT>Exploranium GR820</RAD_INSTRUMENT>
         </ROW>
        </ROWSET>
        '''
        if model_view == 'prov':
            prov_turtle = self.export_rdf('prov', 'text/turtle')
            g = Graph().parse(data=prov_turtle, format='turtle')

            view_html = render_template(
                'survey_prov.html',
                visjs=self._make_vsjs(g),
                prov_turtle=prov_turtle,
            )
        else:  # model_view == 'gapd':
            view_html = render_template(
                'survey_gapd.html',
                survey_no=self.survey_no,
                survey_name=self.survey_name,
                state=self.state,
                operator=self.operator,
                contractor=self.contractor,
                processor=self.processor,
                survey_type=self.survey_type,
                data_types=self.data_types,
                vessel=self.vessel,
                vessel_type=self.vessel_type,
                release_date=self.release_date,
                onshore_offshore=self.onshore_offshore,
                start_date=self.start_date,
                end_date=self.end_date,
                line_km=self.line_km,
                total_km=self.total_km,
                line_spacing=self.line_spacing,
                line_direction=self.line_direction,
                tie_spacing=self.tie_spacing,
                area=self.square_km,
                crystal_volume=self.crystal_volume,
                up_crystal_volume=self.up_crystal_volume,
                digital_data=self.digital_data,
                geodetic_datum=self.geodetic_datum,
                asl=self.asl,
                agl=self.agl,
                mag_instrument=self.mag_instrument,
                rad_instrument=self.rad_instrument,
                wkt_polygon=self.wkt_polygon
            )

        return render_template(
            'page_survey.html',
            view_html=view_html,
            survey_no=self.survey_no,
            end_date=self.end_date,
            survey_type=self.survey_type,
            date_now=datetime.now().strftime('%Y-%m-%d'),
            centroid_lat=self.centroid_lat,
            centroid_lon=self.centroid_lon,
            n_lat=self.n_lat,
            s_lat=self.s_lat,
            w_long=self.w_long,
            e_long=self.e_long,
            gm_key=config.GOOGLE_MAPS_API_KEY
        )


class ParameterError(ValueError):
    pass


if __name__ == '__main__':
    # import controller.model_classes_functions
    # # get the valid views and mimetypes for a Survey
    # survey_views_mimetypes = controller.model_classes_functions.get_classes_views_mimetypes()\
    #     .get('http://pid.geoscience.gov.au/def/ont/gapd#Survey')
    # # get my required controller & mimetype
    # v, f = LDAPI.get_valid_view_and_mimetype(
    #     None,
    #     None,
    #     survey_views_mimetypes
    # )
    # import _config
    # s = SurveyRenderer(921)
    # print(s.render(v, f))
    pass