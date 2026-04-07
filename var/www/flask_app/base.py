from flask.views import MethodView
from flask import request
import json
import yaml
import glob
import os


def get_oidc_user_info():
    """
    Extracts identity data provided by 'OIDCPassIDTokenAs claims'.
    """
    # REMOTE_USER is the standard set by mod_auth_openidc
    username = request.environ.get('REMOTE_USER') or \
               request.environ.get('OIDC_CLAIM_preferred_username') or \
               'unknown_user'

    # Get the groups claim
    raw_groups = request.environ.get('OIDC_CLAIM_groups', '')

    groups = []
    if raw_groups:
        # If the IAM sends a JSON-style list (["a", "b"])
        if raw_groups.startswith('['):
            try:
                import json
                groups = json.loads(raw_groups)
            except:
                groups = [g.strip() for g in raw_groups.split(',')]
        else:
            # If the IAM sends a comma-separated string
            groups = [g.strip() for g in raw_groups.split(',') if g.strip()]
    return {"username": username, "groups": groups}



class FlaskAppBase(MethodView):
    def __init__(self):
        self.CONFIG_DIR = '/var/www/flask_app/config/'
        self.user = get_oidc_user_info()
        self.load_configs()

    def load_configs(self):
        self.app_data = []
        yaml_files = glob.glob(os.path.join(self.CONFIG_DIR, "*.yaml"))
        for filepath in yaml_files:
            filename = os.path.basename(filepath)
            try:
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    data['filename'] = filename
                    self.app_data.append(data)
            except Exception as e:
                app.logger.error(f"Error loading {filename}: {e}")

    def filter_app_data(self):
        user_groups = self.user["groups"]
        out = []
        for data in self.app_data:
            data_groups = data["groups"]
            if set(user_groups).intersection(set(data_groups)):
                out.append(data)
        return out
