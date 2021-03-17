# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
import sys
sys.path.insert(0, 'C:\\Users\\CassanR\\Perso\\Code\\Python\\galery')


# -- Project information -----------------------------------------------------

project = 'Galery'
copyright = '2020, Don Beberto'
author = 'Don Beberto'

# The full version, including alpha/beta/rc tags
release = '1.0'


# -- General configuration ---------------------------------------------------

# Do not add module names in front of classes
add_module_names = False 

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.napoleon', 
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
]

# Add autodoc options
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'member-order': 'bysource',
    #'member-order': 'groupwise',
    #'private-members': False,
}
#autodoc_typehints = 'signature'
autodoc_typehints = 'description'
#autodoc_typehints = 'none'

#autoclass_content = 'both'
autodoc_docstring_signature = True

autodoc_type_aliases = {
    'Options': 'gallery.config.config.Options',
    'Option': 'gallery.config.Option',
}

# Add napoleon options
napoleon_use_ivar = True
napoleon_custom_sections = [
    "Class Attributes",
    "Instance Attributes",
    "Attributes",
    "Methods",
    "Properties",
]
napoleon_use_rtype = True


# Add autodoc_typehints options
#always_document_param_types = True
typehints_fully_qualified = False
set_type_checking_flag = False

# Add intershpinx mappings
intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
    'peewee': ('http://docs.peewee-orm.com/en/latest', '../peewee-modified-objects.inv'),
    'PySide2': ('https://doc.qt.io/qtforpython', '../pyside2-modified-objects.inv'),
}



# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'prev_next_buttons_location': None,
    'collapse_navigation': False,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']



# ===========================================================================================
# 
#   This part is used to remove Object as a base class in class that inherits only from Object
#
# ===========================================================================================

# ClassDocumenter.add_directive_header uses ClassDocumenter.add_line to
#   write the class documentation.
# We'll monkeypatch the add_line method and intercept lines that begin
#   with "Bases:".
# In order to minimize the risk of accidentally intercepting a wrong line,
#   we'll apply this patch inside of the add_directive_header method.



from sphinx.ext.autodoc import ClassDocumenter, _

add_line = ClassDocumenter.add_line
line_to_delete = _(u'Bases: :class:`object`') # % u':class:`object`'

def add_line_no_object_base(self, text, *args, **kwargs):
    if text.strip() == line_to_delete:
        return

    add_line(self, text, *args, **kwargs)

add_directive_header = ClassDocumenter.add_directive_header

def add_directive_header_no_object_base(self, *args, **kwargs):
    self.add_line = add_line_no_object_base.__get__(self)

    result = add_directive_header(self, *args, **kwargs)

    del self.add_line

    return result

ClassDocumenter.add_directive_header = add_directive_header_no_object_base

# ===========================================================================================
# 
#   End of the part removing Object from base classes
#
# ===========================================================================================

def handle_docstring_attributes(app, what, name, obj, options, lines):
    if what == "class":
        modify_attr = False
        modify_meth = False
        for i in range(len(lines)):
            line = lines[i]
            
            if "Attributes" in line:
                modify_attr = True
            if line == '':
                modify_attr = False
            if modify_attr:
                line_split = line.split("**")
                if len(line_split) >= 2:
                    modifier = f" :obj:`{line_split[1]}`"
                    line = "".join([line_split[0], modifier, line_split[2]])
            
            if "Methods" in line:
                modify_meth = True
            if line == '':
                modify_meth = False
            if modify_meth:
                line_split = line.split("**")
                if len(line_split) >= 2:
                    modifier = f" :meth:`{line_split[1]}`"
                    line = "".join([line_split[0], modifier, line_split[2]])
                    
            lines[i] = line
    if name == "gallery.config.config.Config.cell_dimension":
        print("\n")
        print(what)
        print(name)
        print(obj)
        print(options)
        print(lines)
            
           
    for i in range(len(lines)):
        line = lines[i] 
        line = line.replace(" QueryParameters ", " :class:`~gallery.widgets.query.QueryParameters` ")
        line = line.replace(" Config ", " :class:`~gallery.config.config.Config` ")
        line = line.replace(" CellDimension ", " :class:`~gallery.config.config.CellDimension` ")
        line = line.replace("`gallery.config.config.CellDimension`", "`~gallery.config.config.CellDimension`")
        lines[i] = line
    
def blabla(app, what: str, name: str, obj, options, signature, return_annotation):
    if name == "gallery.config.config.Config.cell_dimension":
        print("\n")
        print(what)
        print(name)
        print(obj)
        print(options)
        print(signature)
        print(return_annotation)
        pass
   
def setup(app):
    app.connect('autodoc-process-docstring', handle_docstring_attributes);
    #app.connect('autodoc-process-signature', blabla);
    
#def no_object_description(obj):
#    raise ValueError("No value for data/attributes")
#import sphinx.ext.autodoc
#sphinx.ext.autodoc.object_description = no_object_description