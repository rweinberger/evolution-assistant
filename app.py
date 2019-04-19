from flask import Flask, render_template, request, redirect, url_for
from assistant.ea import EvolutionAssistant
from assistant.sco import Sco, SchemaChange, SchemaChangeSequence
import settings
 
app = Flask(__name__)
 
def get_tables(commit):
    return settings.tables[commit].keys()

def get_vars(commit, table):
    return settings.tables[commit][table]

def group_response(res):
    grouped = {}
    for key in res:
        for value in res.getlist(key):
            splitKey = key.split('#')
            group = splitKey[0]
            index = splitKey[1]
            if index in grouped:
                grouped[index][group] = value
            else:
                grouped[index] = { group: value } 
    return grouped.values()

def create_ea():
    ea = EvolutionAssistant(settings.MODULE,  
                            settings.REPO_DIR,
                            settings.CODE_DIR,
                            settings.SCHEMA_DIR,
                            settings.QUERY_FILES,
                            settings.COMMIT_HASH,
                            settings.MAP_TABLE,
                            2 )
    return ea

def add_scos(scos, ea):
    seq = SchemaChangeSequence()
    for sco_info in scos:
        sco_name = sco_info['sc']
        operand = sco_info['colName'] if 'colName' in sco_info else sco_info['table']
        sc = SchemaChange(sco_name, operand)
        print(sc)
        seq.add(sc)
    total_impact = str(ea.get_impact(seq))
    print(total_impact)

@app.route('/')
def index():
    sco_names = [s.value for s in Sco]
    commit = request.args.get('commit')
    table_names = []
    if commit:
        table_names = get_tables(commit)
    return render_template("index.html", commit = commit, sco_names = sco_names, table_names = table_names)

@app.route('/enter_commit', methods=['POST'])
def enter_commit():
    commit_hash = request.form['commit-hash']
    return redirect(url_for('index', commit = commit_hash))

@app.route('/submit_sc', methods=['POST'])
def submit_sc():
    scos = group_response(request.form)
    ea = create_ea()
    add_scos(scos, ea)
    return 'hi'

@app.route('/get_table_vars', methods=['GET', 'POST'])
def get_table_vars():
    commit = request.json['commit']
    table = request.json['table']
    vars = get_vars(commit, table)
    formatString = '{} ' * len(vars)
    return formatString[:-1].format(*vars) 