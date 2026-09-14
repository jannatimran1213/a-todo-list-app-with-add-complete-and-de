from flask import Flask, request, redirect, url_for, render_template_string
import threading
import time
import urllib.request
import urllib.parse

app = Flask(__name__)

# In‑memory storage for todos
# Each todo is a dict: {'id': int, 'task': str, 'done': bool}

todos = []
next_id = 1

HTML_TEMPLATE = '''
<!doctype html>
<title>Todo List</title>
<h1>Todo List</h1>
<form action="{{ url_for('add') }}" method="post">
    <input type="text" name="task" placeholder="New task" required>
    <input type="submit" value="Add">
</form>
<ul>
{% for todo in todos %}
    <li>
        {% if todo.done %}
            <s>{{ todo.task }}</s>
        {% else %}
            {{ todo.task }}
        {% endif %}
        {% if not todo.done %}
            <form style="display:inline" action="{{ url_for('complete', todo_id=todo.id) }}" method="post">
                <button type="submit">Complete</button>
            </form>
        {% endif %}
        <form style="display:inline" action="{{ url_for('delete', todo_id=todo.id) }}" method="post">
            <button type="submit">Delete</button>
        </form>
    </li>
{% endfor %}
</ul>
''' 

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, todos=todos)

@app.route('/add', methods=['POST'])
def add():
    global next_id
    task = request.form.get('task', '').strip()
    if task:
        todos.append({'id': next_id, 'task': task, 'done': False})
        next_id += 1
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = True
            break
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    global todos
    todos = [t for t in todos if t['id'] != todo_id]
    return redirect(url_for('index'))

# Route to gracefully shut down the server
@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'Server shutting down...'

def run_server():
    # Running with use_reloader=False to avoid spawning extra processes
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    # Start Flask server in a daemon thread so the main program can continue
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    # Give the server a moment to start
    time.sleep(1)
    try:
        # Perform a simple GET request to ensure the server is responding
        with urllib.request.urlopen('http://127.0.0.1:5000/') as response:
            _ = response.read()
        # Trigger shutdown via POST request
        req = urllib.request.Request('http://127.0.0.1:5000/shutdown', method='POST')
        urllib.request.urlopen(req)
    except Exception as e:
        print(f'Error during server interaction: {e}')
    # Wait briefly for the server thread to finish
    server_thread.join(timeout=5)
    print('Todo Flask app started and stopped successfully.')
