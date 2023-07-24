"""
This script runs the BufferSDWebApp application using a development server.
"""

from os import environ
from BufferSDWebApp import app
from flask_talisman import Talisman
SELF = "'self'"
NONE = "'none'"
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': SELF,
        'img-src': NONE,
        'child-src': NONE,
        'frame-ancestors': NONE,
        'form-action': NONE,
        'script-src': [
            SELF,
            "'wasm-unsafe-eval'",
            'pyscript.net/',
            'cdn.jsdelivr.net/'
        ],
        'style-src': [
            SELF,
            'pyscript.net/'
        ],
        'connect-src': [
            SELF,
            'cdn.jsdelivr.net/',
            'pypi.org/',
            'files.pythonhosted.org/'
        ]
    },
    force_https = False
)
if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
