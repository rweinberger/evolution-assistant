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

def reduce_by_maintenance(res):
    grouped = {}
    for maintenance in res.values():
        for maint_type, detail in maintenance.items():
            amount = detail[0]
            if maint_type in grouped:
                grouped[maint_type] += amount
            else:
                grouped[maint_type] = amount
    return grouped

def reduce_by_table(res):
    grouped = {}
    table_totals = {}
    for info, maintenance in res.items():
        (sco, table, var, amount) = info
        if table in grouped:
            grouped[table].append({ (sco, var, amount) : maintenance })
        else:
            grouped[table] = [{ (sco, var, amount) : maintenance }]

        if table in table_totals:
            table_totals[table] += amount
        else:
            table_totals[table] = amount
    return (grouped, table_totals)

def create_ea():
    return EvolutionAssistant(  settings.MODULE,  
                                settings.REPO_DIR,
                                settings.CODE_DIR,
                                settings.SCHEMA_DIR,
                                settings.QUERY_FILES,
                                settings.COMMIT_HASH,
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
    table_names = []
    if commit:
        table_names = get_tables(commit)
    return render_template("index.html", commit = commit, sco_names = sco_names, table_names = table_names)

# @app.route('/result')
# def result():
#     total_impact = request.args.get('total_impact')
#     results = request.args.get('results')
#     maintenance_summary = request.args.get('maintenance_summary')
#     return render_template("result.html", total_impact = total_impact, results = results, maintenance_summary = maintenance_summary)

@app.route('/enter_commit', methods=['POST'])
def enter_commit():
    commit_hash = request.form['commit-hash']
    return redirect(url_for('index', commit = commit_hash))

@app.route('/submit_sc', methods=['POST'])
def submit_sc():
    scos = group_response(request.form)
    ea = create_ea()
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