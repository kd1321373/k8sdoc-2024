# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Kubernetes体験'
copyright = '2024, 佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'
author = '佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'
release = '2024-09-02'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'bizstyle'
html_static_path = ['_static']

extensions = ["sphinx_copybutton", 'myst_parser']

copybutton_prompt_text = r"$ "

sources_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
    '.txt': 'markdown',
}


myst_enable_extensions = [
    #"linkify",
    "substitution",
    "deflist",
    "tasklist",
]
