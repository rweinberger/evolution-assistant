from flask import Flask, render_template, request, redirect, url_for
from assistant.ea import EvolutionAssistant
from assistant.sco import Sco, SchemaChange, SchemaChangeSequence
import settings
 
app = Flask(__name__)
 
def get_tables(commit):
    return settings.tables[commit].keys()

@app.route('/')
def index():
    scos = [s.value for s in Sco]
    commit = request.args.get('commit')
    tables = []
    if commit:
        tables = get_tables(commit)
    return render_template("index.html", commit = commit, scos = scos, tables = tables)

@app.route('/enter_commit', methods=['POST'])
def enter_commit():
    commit_hash = request.form['commit-hash']
    return redirect(url_for('index', commit = commit_hash))

@app.route('/submit_sc', methods=['POST'])
def submit_sc():
    f = request.form
    for key in f.keys():
        for value in f.getlist(key):
            print(key,":",value)
    return 'hi'

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