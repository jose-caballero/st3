from flask import render_template, abort, request
from base import FlaskAppBase
from requestshandler import RequestHandler
import os
import yaml




def cast_types(form_data, params_metadata):
    casted_data = {}
    for key, meta in params_metadata.items():

        # If the parameter is immutable, ignore form_data and use the default value
        if meta.get('immutable'):
            casted_data[key] = meta.get('default')
            continue

        val = form_data.get(key)
        if meta.get('type') == 'boolean':
            casted_data[key] = True if val == 'on' else False
        elif meta.get('type') == 'integer' and val:
            try: casted_data[key] = int(val)
            except: casted_data[key] = val
        elif meta.get('type') == 'array' and val:
            casted_data[key] = [i.strip() for i in val.split(',')]
        elif val == '' and not meta.get('required'):
            casted_data[key] = meta.get('default')
        else:
            casted_data[key] = val
    return casted_data


class ActionFormView(FlaskAppBase):

    def __init__(self):
        self.metadata = None
        super(ActionFormView, self).__init__()
    
    def _get_metadata(self, action_name):
        """Helper method to handle common setup logic."""
        yaml_path = os.path.join(self.CONFIG_DIR, f"{action_name}.yaml")

        if not os.path.exists(yaml_path):
            abort(404)

        with open(yaml_path, 'r') as f:
            self.metadata = yaml.safe_load(f)


    def _authorised_form(self):
        user_groups = self.user["groups"]
        data_groups = self.metadata["groups"]
        return set(user_groups).intersection(set(data_groups)) != set()

    def get(self, action_name):
        
        if not self.metadata:
            self._get_metadata(action_name)

        if not self._authorised_form():
            return "You do not have required authorisations for this action", 403

        return render_template(
            'form.html',
            action_name=self.metadata.get('name', action_name),
            description=self.metadata.get('description', ''),
            params=self.metadata.get('parameters', {}),
            enabled=self.metadata.get('enabled', True),  # Pass the enabled flag
            result=None,
            user=self.user
        )

    def post(self, action_name):
        
        if not self.metadata:
            self._get_metadata(action_name)

        if not self._authorised_form():
            return "You do not have required authorisations for this action", 403

        # Guard clause: prevent execution if action is disabled
        if not self.metadata.get('enabled', True):
            return "This action is currently disabled and cannot be executed.", 400

        params = self.metadata.get('parameters', {})
        result = None

        try:
            from run import run
            # Handle payload and auditing
            payload = cast_types(request.form, params)
            #payload['_triggered_by'] = self.user['username']
            result = run(payload)

            action_name = self.metadata.get('name', action_name)
            username = self.user['username']
            req = RequestHandler()
            req.create(action_name, payload, username)

        except Exception as e:
            result = {"status": "error", "message": str(e)}

        #result_html = "<h1>Success!</h1><p>This was rendered <strong>as is</strong>.</p>"
        return render_template(
            'form.html',
            action_name=self.metadata.get('name', action_name),
            description=self.metadata.get('description', ''),
            params=params,
            enabled=self.metadata.get('enabled', True), # Ensure flag remains in the view after POST
            result=result,
            # result_html=result_html,
            user=self.user
        )
