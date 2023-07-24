"""
The flask application package.
"""
from flask import Flask, render_template
app = Flask(__name__)

import BufferSDWebApp.views
