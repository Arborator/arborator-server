#!/usr/bin/python
from wsgiref.handlers import CGIHandler
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from main import app
import cgitb
cgitb.enable()

CGIHandler().run(app)