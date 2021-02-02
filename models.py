from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.objects import Ref
from dotenv  import load_dotenv
from typing import Dict
import os

load_dotenv()

client = FaunaClient(secret=os.getenv('FAUNA_SECRET'))
# indexes = client.query(q.paginate(q.indexes()))

# print(indexes)

class User:
    def __init__(self) -> None:
        self.collection = q.collection('users')

    def create_user(self, data) -> Dict[str, str]:
        new_data = client.query(
            q.create(
                self.collection,
                {'data': data}
            )
        )
        new_data['data']['id'] = new_data['ref'].value['id']
        return new_data['data']

    def get_user(self, id):
        user = client.query(
            q.get(
                q.ref(q.collection('users'), id)
            )
        )
        return None if user.get('errors') else user['data']

    def get_user_by_email(self, email):
        user = client.query(
            q.get(q.match(q.index('user_by_email'), email))
        )
        return None if user.get('errors') else user['data']

class Todo:
    def __init__(self) -> None:
        self.collection = q.collection('todos')

    def create_todo(self, user_id, data) -> Dict[str, str]:
        new_todo = client.query(
            q.create(
                self.collection,
                {'data': {**data, 'user_id': user_id}}
            )
        )
        new_todo['data']['id']=new_todo['ref'].value['id']
        return new_todo['data']

    def get_todo(self, id):
        todo = client.query(
            q.get(
                q.ref(self.collection, id)
            )
        )
        return None if todo.get('errors') else todo['data']
 
    def get_todos(self, user_id):
        # client.query(
        #     q.map_(
        #         q.paginate(q.match(q.index('todo_by_user_id'), user_id)),
        #         q.lambda_('todo', q.get(q.var('todo')))
        #     )
        # )
        todos =  client.query(
            q.get(q.match(q.index('todo_by_user_id'), user_id))
        ) 
        return [
            {
                'id': todo['id'], 
                'name': todo['name'], 
                'is_completed': todo['is_completed']
            } for todo in todos
        ]

    def update_todo(self, id, data):
        return client.query(
            q.update(
                q.ref(self.collection, id),
                {'data': data}
            )
        )['data']

    def delete_todo(self, id):
        data = client.query(
            q.delete(
                q.ref(self.collection, id)
            )
        )
        return data['data']

    def __repr__(self) -> str:
        f''