from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.objects import Ref
from faunadb.errors import BadRequest, NotFound
from dotenv  import load_dotenv
from typing import Dict
import os, secrets

load_dotenv()

client = FaunaClient(secret=os.getenv('FAUNA_SECRET'))
indexes = client.query(q.paginate(q.indexes()))

print(indexes)

class User:
    def __init__(self) -> None:
        self.collection = q.collection('users')

    def create_user(self, data) -> Dict[str, str]:
        new_data = client.query(
            q.create(
                self.collection,
                {'data': {**data, 'id': secrets.token_hex(12)}}
            )
        ) 
        return new_data['data']

    def get_user(self, id):
        try:
            user = client.query(
                q.get(q.match(q.index('user_by_id'), id))
            )
        except NotFound:
            return None
        return None if user.get('errors') else user['data']

    def get_user_by_email(self, email):
        try:
            user = client.query(
                q.get(q.match(q.index('user_by_email'), email))
            )
        except NotFound:
            return None
        return None if user.get('errors') else user['data']

class Todo:
    def __init__(self) -> None:
        self.collection = q.collection('todos')

    def create_todo(self, user_id, data) -> Dict[str, str]:
        new_todo = client.query(
            q.create(
                self.collection,
                {'data': {**data, 'user_id': user_id, 'id': secrets.token_hex(12)}}
            )
        )
        return new_todo['data']

    def get_todo(self, id):
        try:
            todo = client.query(
                q.get(q.match(q.index('todo_by_id'), id))
            )
        except NotFound:
            return None
        return None if todo.get('errors') else todo 
 
    def get_todos(self, user_id):
        try:
            todos=client.query(q.paginate(q.match(q.index("todo_by_user_id"), user_id)))
            return [
                        client.query(
                            q.get(q.ref(q.collection("todos"), todo.id()))
                        )['data']  
                        for todo in todos['data']
                    ] 
        except NotFound:
            return None  

    def update_todo(self, id, data):
        try:
            return client.query(
                q.update(
                    q.ref(q.collection("todos"), id),
                    {'data': data}
                )
            )['data']
        except NotFound:  
            return 'Not found'

    def delete_todo(self, id):
        try:
            return client.query(q.delete(q.ref(q.collection("todos"), id)))['data']
        except NotFound:
            return None
