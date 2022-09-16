"""
'app' in this module is a WSGI app.

This is the convention used by boring-serverless to
locate the entrypoint for an application.
"""
import sys
sys.stdout = sys.stderr

from rajdhani.app import app
