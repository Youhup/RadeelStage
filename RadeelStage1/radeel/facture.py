from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from radeel.db import get_db

from radeel.auth import login_required

bf = Blueprint('facture', __name__, url_prefix='/facture')

@bf.before_request
@login_required  
def before_request():
    pass 

@bf.route('/')
def index():
    db = get_db()
    factures = db.execute(
        'SELECT * FROM factures ORDER BY date_ DESC'
    ).fetchall()
    return render_template('factures/index.html', factures= factures )


    