import operator
import string
from optparse import OptionParser
from sqlalchemy import create_engine, MetaData
from sadisplay import describe, render, __version__
import pydot
from sqlalchemy.engine.url import URL
import json

from flask import Flask, Markup, render_template, request
from GoFourth import *

app = Flask(__name__)

@app.route("/")
def index():
    
    return render_template('index.html')

@app.route("/schema/<db>")
def schema(db):
    
    url = str(URL("sqlite", database = 'Chinook_Sqlite.sqlite'))
    engine = create_engine(url)
    meta = MetaData()

    meta.reflect(bind=engine)
    
    tables = set(meta.tables.keys())

    desc = describe(map(lambda x: operator.getitem(meta.tables, x), tables))
    graph_file = getattr(render, 'dot')(desc)
    #what = json.loads(graph_file)
    #graph_file = json.dump(what)
    #return graph_file
    return render_template('viewer.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
    
    
    
    url = str(URL("sqlite", database = 'Chinook_Sqlite.sqlite'))
    engine = create_engine(url)
    meta = MetaData()

    meta.reflect(bind=engine)
    
    tables = set(meta.tables.keys())

    desc = describe(map(lambda x: operator.getitem(meta.tables, x), tables))
    graph_file = getattr(render, 'dot')(desc)    
        
    with open('new.dot', 'w') as file:
        file.write(graph_file)
    
    graph = pydot.Dot(graph_file)
    graph = pydot.graph_from_dot_file('new.dot')
    graph.write_png('somefile.png')
    print "done"