from flask import Flask, render_template, request, redirect, url_for
import threading
from calmind.main import CalMindApp
from calmind.config import Config

app = Flask(__name__)

# Initialize CalMindApp (can be done once or per request depending on desired behavior)
# For simplicity, initializing once here. If config changes frequently, re-initialize.
calmind_app_instance = CalMindApp()

@app.route('/')
def index():
    config = Config()
    users = config.get_users_config()
    return render_template('index.html', users=users)

@app.route('/run_report/<user_name>')
def run_report(user_name):
    config = Config()
    users_config = config.get_users_config()
    user_to_run = next((u for u in users_config if u.get('name') == user_name), None)

    if user_to_run:
        # Run the report in a separate thread to avoid blocking the web server
        # In a production app, you'd use a proper task queue (e.g., Celery)
        def run_task():
            # Re-initialize CalMindApp for each task to ensure fresh config and state
            task_app = CalMindApp()
            task_app._initialize_llm() # Initialize LLM for the task
            task_app._initialize_email_sender() # Initialize email sender for the task
            task_app.run_for_user(user_to_run)

        thread = threading.Thread(target=run_task)
        thread.start()
        return f"Report generation for {user_name} started in background. Check your email/reports folder soon!"
    else:
        return "User not found in configuration.", 404

@app.route('/run_all_reports')
def run_all_reports():
    def run_task():
        task_app = CalMindApp()
        task_app.run()

    thread = threading.Thread(target=run_task)
    thread.start()
    return "All reports generation started in background. Check your email/reports folder soon!"

if __name__ == '__main__':
    app.run(debug=True)
