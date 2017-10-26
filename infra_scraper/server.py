
from flask import Flask, redirect, render_template, jsonify

from .main import InfraScraper

import logging

logger = logging.getLogger(__name__)


def run():
    app = Flask(__name__, static_folder='./assets/static')

    @app.route('/')
    def index():
        scraper = InfraScraper()
        config = scraper.get_global_config()
        return render_template('index.html',
                               config=config)

    @app.route('/layout/<name>/<layout>')
    def topology_layout(name, layout):
        scraper = InfraScraper()
        config = scraper.get_config(name)
        return render_template('layout.html',
                               name=name,
                               config=config,
                               layout=layout)

    @app.route('/api/<name>/scrape')
    def scrape_data(name=None):
        scraper = InfraScraper()
        scraper.scrape_data(name)
        return redirect('.')

    @app.route('/api/<name>')
    def topology_data(name=None):
        scraper = InfraScraper()
        data = scraper.get_cached_data(name, 'vis')
        return jsonify(data)

    @app.route('/api/<name>/hier')
    def hierarchy_topology_data(name=None):
        scraper = InfraScraper()
        data = scraper.get_cached_data(name, 'vis-hier')
        return jsonify(data)

    app.run(host='0.0.0.0', port=8076)
