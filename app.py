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
        if key != 'commit_hash':
            for value in res.getlist(key):
                splitKey = key.split('#')
                group = splitKey[0]
                index = splitKey[1]
                if index in grouped:
                    grouped[index][group] = value
                else:
                    grouped[index] = { group: value }
    return grouped.values()

def create_ea(commit_hash):
    return EvolutionAssistant(  settings.info[commit_hash]['MODULE'],  
                                settings.REPO_DIR,
                                settings.CODE_DIR,
                                settings.info[commit_hash]['SCHEMA_DIR'],
                                settings.info[commit_hash]['QUERY_FILES'],
                                commit_hash,
                                settings.MAP_TABLE,
                                2 )

def get_seq(scos):
    new_seq = SchemaChangeSequence()
    for sco_info in scos:
        sco_name = sco_info['sc']
        table = sco_info['table']
        operand = sco_info['colName'] if 'colName' in sco_info else table
        sc = SchemaChange(sco_name, table, operand)
        new_seq.add(sc)
    return new_seq

@app.route('/')
def index():
    sco_names = [s.value for s in Sco]
    commit = request.args.get('commit')
    commit_hashes = settings.tables.keys()
    table_names = []
    if commit:
        table_names = get_tables(commit)
    return render_template("index.html", commit = commit, sco_names = sco_names, table_names = table_names, commit_hashes = commit_hashes)

@app.route('/enter_commit', methods=['POST'])
def enter_commit():
    commit_hash = request.form['commit-hash']
    return redirect(url_for('index', commit = commit_hash))

@app.route('/submit_sc', methods=['POST'])
def submit_sc():
    commit_hash = request.form['commit_hash']
    scos = group_response(request.form)
    ea = create_ea(commit_hash)
    seq = get_seq(scos)
    (total_impact, overall_breakdown, table_breakdown, table_to_sco, sco_details) = ea.get_impact(seq)
    # summary = reduce_by_maintenance(results)
    # (grouped, table_totals) = reduce_by_table(results)
    headers = ['schema_maintenance', 'query_maintenance', 'app_maintenance', 'map_maintenance', 'simple_add', 'TOTAL']
    return render_template( "result.html", 
                            total_impact = total_impact, 
                            overall_breakdown = overall_breakdown,
                            table_breakdown = table_breakdown, 
                            table_to_sco = table_to_sco, 
                            sco_details = sco_details,
                            headers = headers )

@app.route('/get_table_vars', methods=['GET', 'POST'])
def get_table_vars():
    commit = request.json['commit']
    table = request.json['table']
    vars = get_vars(commit, table)
    formatString = '{} ' * len(vars)
    return formatString[:-1].format(*vars) 

@app.route('/show_file', methods=['GET', 'POST'])
def show_file():
    filename = request.args.get('filename')
    line_num = request.args.get('line')
    # line_num = int(line_num)

    lines = []
    f = open(filename, 'r')
    line = f.readline()

    while line:
        lines.append(line)
        line = f.readline()

    f.close()
    return render_template( "file.html", lines=lines, line_num = line_num )