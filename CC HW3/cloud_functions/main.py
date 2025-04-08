import functions_framework
from google.cloud import datastore

@functions_framework.http
def reset_completed_tasks(request):
    client = datastore.Client(project="daily-goal-tracker-456008")
    query = client.query(kind='Goal')
    query.add_filter('completed', '=', True)
    completed_tasks = list(query.fetch())

    print(f"Am găsit {len(completed_tasks)} taskuri completate.")

    for task in completed_tasks:
        print(f"Aș șterge: {task['task']} (ID: {task.key.id})")

    return ('Testul a rulat', 200)
