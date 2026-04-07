from base import FlaskAppBase
from flask import render_template


class IndexView(FlaskAppBase):
    def get(self):
        # Your logic for the homepage goes here
        app_data_filtered = self.filter_app_data()
        return render_template('index.html', entries=app_data_filtered, user=self.user)
    
