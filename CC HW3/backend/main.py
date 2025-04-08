from flask import Flask, send_from_directory, request, jsonify
import os
import datetime
from google.cloud import datastore
from google.cloud import storage
import uuid
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)
datastore_client = datastore.Client(project="daily-goal-tracker-456008")
storage_client = storage.Client(project="daily-goal-tracker-456008")
BUCKET_NAME = 'daily-goal-tracker-imagini'


@app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    unique_filename = f"{uuid.uuid4()}_{image.filename}"

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(unique_filename)
    blob.upload_from_file(image, content_type=image.content_type)

    url = f"https://storage.googleapis.com/{BUCKET_NAME}/{unique_filename}"

    task_id = request.form.get("task_id")
    if task_id:
        key = datastore_client.key('Goal', int(task_id))
        task = datastore_client.get(key)
        if task:
            task["image_url"] = url
            datastore_client.put(task)

    return jsonify({
        'message': 'Upload successful',
        'image_url': url
    }), 200

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/goals', methods=['POST'])
def add_goal():
    data = request.get_json()
    task = data.get('task')
    deadline_str = data.get('deadline')
    deadline = datetime.datetime.fromisoformat(deadline_str) if deadline_str else None

    key = datastore_client.key('Goal')
    goal = datastore.Entity(key=key)
    goal.update({
        'task': task,
        'timestamp': datetime.datetime.utcnow(),
        'deadline': deadline,
        'completed': False,
        'image_url': ''
    })
    datastore_client.put(goal)

    return jsonify({'id': goal.key.id, 'task': task}), 201

@app.route('/api/goals', methods=['GET'])
def list_goals():
    query = datastore_client.query(kind='Goal')
    goals = list(query.fetch())

    def serialize_goal(goal):
        return {
            'id': goal.key.id,
            'task': goal.get('task'),
            'timestamp': goal.get('timestamp').isoformat() if goal.get('timestamp') else None,
            'deadline': goal.get('deadline').isoformat() if goal.get('deadline') else None,
            'completed': goal.get('completed'),
            'image_url': goal.get('image_url')
        }
    return jsonify([serialize_goal(g) for g in goals]), 200

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    key = datastore_client.key('Goal', goal_id)
    goal = datastore_client.get(key)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    data = request.get_json()
    if 'task' in data:
        goal['task'] = data['task']
    if 'completed' in data:
        goal['completed'] = data['completed']
    if 'deadline' in data:
        deadline_str = data['deadline']
        goal['deadline'] = datetime.datetime.fromisoformat(deadline_str) if deadline_str else None

    datastore_client.put(goal)
    return jsonify({'message': 'Goal updated successfully'}), 200

@app.route('/api/update-goal-image/<int:goal_id>', methods=['PUT'])
def update_goal_image(goal_id):
    data = request.get_json()
    image_url = data.get('image_url')
    key = datastore_client.key('Goal', goal_id)
    goal = datastore_client.get(key)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    goal['image_url'] = image_url
    datastore_client.put(goal)
    return jsonify({'message': 'Image URL updated successfully'}), 200


@app.route('/api/submit', methods=['POST'])
def submit_goal():
    data = request.get_json()
    return jsonify({'received': data})

if __name__ == '__main__':
    print("Flask pornește...")
    app.run(host='0.0.0.0', port=8080, debug=True)