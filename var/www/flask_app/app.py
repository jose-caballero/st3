import os
import glob
import yaml
import json
from flask import Flask, render_template, abort, request
from flask.views import MethodView

from base import FlaskAppBase
from indexview import IndexView
from actionview import ActionFormView

app = Flask(__name__)


# --- DEBUG ROUTE ---
@app.route('/debug-auth')
def debug_auth():
    """Returns all OIDC related environment variables for troubleshooting."""
    oidc_vars = {k: v for k, v in request.environ.items() if k.startswith('OIDC_') or k == 'REMOTE_USER'}
    return render_template('form.html', 
                           action_name="Auth Debug", 
                           description="Listing OIDC Environment Variables",
                           params={}, 
                           result={"status": "info", "message": "Check the payload below", "received_payload": oidc_vars})


# ============================================================================== 
# register the routes
# ============================================================================== 
app.add_url_rule('/form/<action_name>', view_func=ActionFormView.as_view('action_form'))
app.add_url_rule('/', view_func=IndexView.as_view('index'))



if __name__ == '__main__':
    app.run()
