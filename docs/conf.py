# -*- coding: utf-8 -*-

import sys
import os

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
currpath = os.path.dirname(os.path.abspath(__file__))
pyespath = os.path.join(currpath, "pyes")
sys.path.append(pyespath)

#import settings
#from django.core.management import setup_environ
# Commenting out the following line as it is not used.
#from django.conf import settings as dsettings
#setup_environ(settings)
#dsettings.configure()
import pyes as info
sys.path.append(os.path.join(os.path.dirname(__file__), "_ext"))

# -- General configuration -----------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'djangodocs']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['.templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'PyES Documentation'
copyright = u'2010, Alberto Paro and Elastic Search. All Rights Reserved.'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = info.__version__
# The full version, including alpha/beta/rc tags.
release = info.version_with_meta()

exclude_trees = ['.build']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'trac'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_use_smartypants = True

# If false, no module index is generated.
html_use_modindex = True

# If false, no index is generated.
html_use_index = True

latex_documents = [
  ('index', 'pyes.tex', ur'PyES Documentation',
   ur'Elastic Search', 'manual'),
]
