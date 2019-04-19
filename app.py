from flask import Flask, render_template, request, redirect, url_for
from assistant.ea import EvolutionAssistant
from assistant.sco import Sco, SchemaChange, SchemaChangeSequence
import settings
 
app = Flask(__name__)
 
def get_tables(commit):
    return settings.tables[commit].keys()

def get_vars(commit, table):
    return settings.tables[commit][table]

@app.route('/')
def index():
    sco_names = [s.value for s in Sco]
    commit = request.args.get('commit')
    table_names = []
    if commit:
        tables = get_tables(commit)
    return render_template("index.html", commit = commit, sco_names = sco_names, table_names = table_names)

@app.route('/enter_commit', methods=['POST'])
def enter_commit():
    commit_hash = request.form['commit-hash']
    return redirect(url_for('index', commit = commit_hash))

@app.route('/submit_sc', methods=['POST'])
def submit_sc():
    f = request.form
    grouped = {}
    for key in f:
        for value in f.getlist(key):
            splitKey = key.split('#')
            group = splitKey[0]
            index = splitKey[1]
            if index in grouped:
                grouped[index][group] = value
            else:
                grouped[index] = { group: value } 
    scos = grouped.values()
    return 'hi'

@app.route('/get_table_vars', methods=['GET', 'POST'])
def get_table_vars():
    commit = request.json['commit']
    table = request.json['table']
    vars = get_vars(commit, table)
    formatString = '{} ' * len(vars)
    return formatString[:-1].format(*vars) 

# ea = EvolutionAssistant(settings.MODULE,  
#                         settings.REPO_DIR,
#                         settings.CODE_DIR,
#                         settings.SCHEMA_DIR,
#                         settings.QUERY_FILES,
#                         settings.COMMIT_HASH,
#                         settings.MAP_TABLE,
#                         0 )

# sc1 = SchemaChange(Sco.ADD_COLUMN, "new_column")
# sc2 = SchemaChange(Sco.DROP_TABLE, "national_freight")
# sc3 = SchemaChange(Sco.DROP_COLUMN, "contract_type")
# sc4 = SchemaChange(Sco.RENAME_TABLE, "national_freight")
# sc5 = SchemaChange(Sco.RENAME_COLUMN, "contract_type")
# seq = SchemaChangeSequence()
# seq.add_all(sc1, sc2, sc3, sc4, sc5)
# total_impact = str(ea.get_impact(seq))