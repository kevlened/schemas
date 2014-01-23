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
    
    dbs = [{'name': d.name,
            'id': d.id,
            'alias':d.alias,
            'host':d.host,
            'engine':d.engine} for d in db]
    
    return json.dumps(dbs)

@app.route("/add_schema", methods=['POST'])
def add_schema():
    engine = create_engine('sqlite:///databases.db')
    DBSession = sessionmaker(bind=engine)
    
    session = DBSession()
    
    db = json.loads(request.data)
    if db['alias'] == '':
        db['alias'] = db['name']

    new_db = Database(name=db['name'], alias=db['alias'], engine=db['engine'], username=db['username'], password=db['password'], host=db['host'], port=db['port'])
    session.add(new_db)
    session.commit()
    
    
    data = {'status': 'success',
            'result':  {'name': new_db.name,
                        'id': new_db.id,
                        'alias': new_db.alias,
                        'host': new_db.host,
                        'port': new_db.port,
                        'engine': new_db.engine}
            } 
    return json.dumps(data)

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
    db = session.query(Database).filter(Database.id == db).first()
    
    if db is None:
        raise Exception("There are no databases identified by " + db)
    
    # Get the dot file
    url = str(URL(db.engine, database = db.name))
    engine = create_engine(url)
    meta = MetaData()

    meta.reflect(bind=engine)
    
    tables = set(meta.tables.keys())

    desc = describe(map(lambda x: operator.getitem(meta.tables, x), tables))
    graph_file = to_dot(desc)
    with open('new.dot', 'w') as file:
        file.write(graph_file)
    return graph_file

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
         
        #new_db = Database(name='Chinook_Sqlite.sqlite', engine='sqlite')
        #session.add(new_db)
        session.commit()    
    
    app.run()