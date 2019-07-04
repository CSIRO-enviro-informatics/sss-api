import logging
import _config as conf
from flask import Flask
from controller import pages, classes, oai
from flask_compress import Compress

# Compression defaults
COMPRESS_MIMETYPES = ['application/vnd.google-earth.kml+xml',
                      'text/html', 
                      'text/css', 
                      'text/xml', 
                      'application/json', 
                      'application/javascript'
                      ]
COMPRESS_LEVEL = 0
COMPRESS_MIN_SIZE = 2000 # Don't bother compressing small responses

def configure_app_compression(app):
    '''
    Helper function to set app config parameters
    '''
    app.config['COMPRESS_MIMETYPES'] = COMPRESS_MIMETYPES 
    app.config['COMPRESS_LEVEL'] = COMPRESS_LEVEL 
    app.config['COMPRESS_MIN_SIZE'] = COMPRESS_MIN_SIZE 

app = Flask(__name__, template_folder=conf.TEMPLATES_DIR, static_folder=conf.STATIC_DIR)

if COMPRESS_LEVEL > 0:
    configure_app_compression(app)
    Compress(app)

app.register_blueprint(pages.pages)
app.register_blueprint(classes.classes)
app.register_blueprint(oai.oai_)


# run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=conf.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    app.run(debug=conf.DEBUG)
