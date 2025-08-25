
import os
import json
from flask import Flask, render_template, request
from calmind.main import CalMindApp
from calmind.config import Config

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'))

# Initialize CalMindApp
calmind_app_instance = CalMindApp()
calmind_app_instance._initialize_llm()
calmind_app_instance._initialize_email_sender()

@app.route('/', methods=['GET', 'POST'])
def index():
    config = Config()
    users_config = config.get_users_config()
    users = [user.model_dump() for user in users_config]
    report_content = None

    if request.method == 'POST':
        user_name = request.form.get('user')
        source_name = request.form.get('source')
        user_to_run = next((u for u in users_config if u.name == user_name), None)

        if user_to_run:
            report_content = calmind_app_instance.run_for_user(user_to_run, source_name)

    return render_template('index.html', users=users, report_content=report_content)

if __name__ == '__main__':
    app.run(debug=True)
