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
    #graph_file = getattr(render, 'dot')(desc)
    #what = json.loads(graph_file)
    #graph_file = json.dump(what)
    #return graph_file
    graph_file = to_dot(desc)
    with open('new.dot', 'w') as file:
        file.write(graph_file)
    return render_template('viewer.html')

def to_dot(desc):
    
    result = ["""
    digraph G {
        graph[overlap=false, splines=true]
    
        fontsize = 8

        node [
            fontsize = 8
            shape = record
        ];

        edge [
            fontsize = 8
        ];
    """]
    
    classes, relations, inherits = desc
    
    CLASS_TEMPLATE = """
        "{name}" [label="{{\\
            {name}|\\
            {props}
        }}"]
    """
    
    COLUMN_PROPERTY_TEMPLATE = "{name} : {type}\\l\\"
    
    for cls in classes:
        
        colsprops = []
        
        for col in cls['cols']:
            colsprops.append(COLUMN_PROPERTY_TEMPLATE.format(type=col[0], name=col[1]))
            
        props = '\n'.join(colsprops)
        rendered = CLASS_TEMPLATE.format(name=cls['name'], props=props)

        result.append(rendered)

    EDGE_INHERIT = "\tedge [\n\t\tarrowhead = empty\n\t]"
    INHERIT_TEMPLATE = "\t%(child)s -> %(parent)s \n"

    EDGE_REL = "\tedge [\n\t\tarrowhead = ediamond\n\t\tarrowtail = open\n\t]"
    RELATION_TEMPLATE = "\t\"%(from)s\" -> \"%(to)s\" [label = \"%(by)s\"]"

    result += [EDGE_INHERIT]
    for item in inherits:
        result.append(INHERIT_TEMPLATE % item)

    result += [EDGE_REL]
    for item in relations:
        result.append(RELATION_TEMPLATE % item)

    result += [
        '}'
    ]

    r = '\n'.join(result)
    return r

if __name__ == "__main__":
    app.debug = True
    #schema("hey")
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