from flask import Flask, render_template
from assistant.ea import EvolutionAssistant
from assistant.sco import Sco, SchemaChange, SchemaChangeSequence
import settings
 
app = Flask(__name__)
 
@app.route('/')
def index():
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
    scos = [s.value for s in Sco]
    return render_template("index.html", scos = scos)