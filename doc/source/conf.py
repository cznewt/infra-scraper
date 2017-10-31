# -*- coding: utf-8 -*-
#
# InfraScraper documentation build configuration file
#
import sys
import os

# import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.pngmath',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'InfraScraper'
copyright = u'2017, Aleš Komárek'
version = '0.2'
release = '0.2.0'
exclude_patterns = []
pygments_style = 'sphinx'
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'collapse_navigation': False,
    'display_version': False,
}


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    ('index', 'infra_scraper.tex', u'InfraScraper Documentation',
     u'InfraScraper Team', 'manual'),
]

man_pages = [
    ('index', 'infra_scraper', u'InfraScraper Documentation',
     [u'Komarek'], 1)
]
