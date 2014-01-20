import operator
import string
from optparse import OptionParser
from sqlalchemy import create_engine, MetaData
from sadisplay import describe, render, __version__
import pydot
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from models import Base, Database
import json, os

from flask import Flask, Markup, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    
    return render_template('index.html')

@app.route("/schemas")
def schemas():
    # Identify the parameters for the database
    engine = create_engine('sqlite:///databases.db')
    Base.metadata.bind = engine  
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    db = session.query(Database).all()
    
    dbs = [d.name for d in db]
    
    return json.dumps(dbs)

@app.route("/schemas/<db>")
def schema(db):
    dot = get_dot_schema(db)
    return render_template('viewer.html', dot_file=dot)

@app.route("/schemas/<db>/dot")
def dot_schema(db):
    return get_dot_schema(db)    
    
def get_dot_schema(db):
    # Identify the parameters for the database
    engine = create_engine('sqlite:///databases.db')
    Base.metadata.bind = engine  
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    db = session.query(Database).filter(Database.name == db).all()
    
    if len(db) == 1:
        db = db[0]
    elif len(db) == 0:
        raise Exception("There are no databases identified by " + db) 
    else:
        raise Exception("There are multiple databases identified by " + db) 
    
    # Get the dot file
    url = str(URL(db.engine, database = db.name))
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
#    with open('new.dot', 'w') as file:
#        file.write(graph_file)
    with open('new.dot', 'w') as file:
        file.write(graph_file)
    return graph_file
    #return render_template('viewer.html')

def to_dot(desc):
    
    result = ["""
    digraph G {
        graph[overlap=false, splines=true];
    
        fontsize = 8;

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
        }}"];
    """
    
    COLUMN_PROPERTY_TEMPLATE = "{name} : {type}\\l\\"
    
    for cls in classes:
        
        colsprops = []
        
        for col in cls['cols']:
            colsprops.append(COLUMN_PROPERTY_TEMPLATE.format(type=col[0], name=col[1]))
            
        props = '\n'.join(colsprops)
        rendered = CLASS_TEMPLATE.format(name=cls['name'], props=props)

        result.append(rendered)

    EDGE_INHERIT = "\tedge [\n\t\tarrowhead = empty\n\t];"
    INHERIT_TEMPLATE = "\t%(child)s -> %(parent)s; \n"

    EDGE_REL = "\tedge [\n\t\tarrowhead = odot\n\t\tarrowtail = crow\n\tdir = both\n\t];"
    RELATION_TEMPLATE = "\t\"%(from)s\" -> \"%(to)s\" [label = \"%(by)s\"];"

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
    
    if os.path.exists('databases.db'):
        engine = create_engine('sqlite:///databases.db')
    else:
        engine = create_engine('sqlite:///databases.db')
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        
        session = DBSession()
         
        new_db = Database(name='Chinook_Sqlite.sqlite', engine='sqlite')
        session.add(new_db)
        session.commit()    
    
    app.run()