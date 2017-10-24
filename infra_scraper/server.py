
from flask import Flask
from flask import render_template
from flask import jsonify

from .main import InfraScraper

import logging

logger = logging.getLogger(__name__)


def run():
    app = Flask(__name__, static_folder='./assets/static')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/layout/<name>')
    def layout(name=None):
        return render_template('layout.html', name=name)

    @app.route('/api/<name>')
    def topology_data(name=None):
        scraper = InfraScraper()
        data = scraper.get_data(name, 'vis', 'raw')
        return jsonify(data)

    app.run(host='0.0.0.0', port=8076)
