from flask import render_template, request
from base import FlaskAppBase
from requestshandler import RequestsManager

class HistoryView(FlaskAppBase):
    def get(self):
        # 1. Fetch all requests using the existing manager
        requests_manager = RequestsManager()
        requests_list = requests_manager.get_all()
        
        # 2. Extract data into a list of dictionaries for easier sorting
        history_data = []
        for req in requests_list:
            try:
                # req.data returns a Data object as per requestshandler.py
                d = req.data
                history_data.append({
                    "action": d.action,
                    "user": d.user,
                    "status": d.status,
                    "request_id": d.request_id # Include request_id for the link
                })
            except (FileNotFoundError, KeyError, Exception):
                # Handle cases where a file might be deleted or corrupted during read
                continue

        # 3. Handle Sorting Logic
        sort_column = request.args.get('sort', 'action')  # Default sort by action
        sort_order = request.args.get('order', 'asc')    # Default order ascending
        
        # Ensure we only sort by valid columns to avoid issues
        if sort_column in ['action', 'user', 'status']:
            history_data.sort(
                key=lambda x: x[sort_column].lower(), 
                reverse=(sort_order == 'desc')
            )

        return render_template(
            'history.html', 
            history=history_data, 
            current_sort=sort_column, 
            current_order=sort_order,
            user=self.user
        )

class RequestDetailView(FlaskAppBase):
    def get(self, request_id):
        requests_manager = RequestsManager()
        req_handler = requests_manager.get_by_id(request_id)
        if not req_handler:
            abort(404)

        # Access the raw dictionary from the Data object
        data = req_handler.data.data
        return render_template('request_detail.html', req=data, user=self.user)
