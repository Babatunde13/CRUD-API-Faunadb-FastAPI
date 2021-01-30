from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.objects import Ref
from dotenv  import load_dotenv
import os

load_dotenv()

client = FaunaClient(secret=os.getenv('FAUNA_SECRET'))

indexes = client.query(q.paginate(q.indexes()))

print(indexes)

class User:
    def __init__(self) -> None:
        self.collection = q.collection('users')

    def create_user(self, data):
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
        return user['data']

    def get_users(self):
        pass

    def update_user(id, data):
        pass

    def delete_user(self):
        pass

    def __repr__(self) -> str:
        f''


class Todo:
    def __init__(self) -> None:
        self.collection = q.collection('todos')

    def create_todo(self, user_id, data):
        new_todo = client.query(
            q.create(
                self.collection,
                {'data': data}
            )
        )
        new_todo['data']['id'] = new_todo['ref'].value['id']
        user_todos = client.query(
            q.get(
                q.ref(self.collection, user_id)
            )
        )['data']['todos']
        todo_data = {'todo_ids': [*user_todos, new_todo['data']['id']]} if user_todos \
                else {'todo_ids': [new_todo['data']['id']]}
        client.query(
            q.update(
                q.ref(self.collection, user_id),
                todo_data
            )
        )
        return new_todo

    def get_todo(self, user_id, id):
        return client.query(
            q.get(
                q.ref(self.collection, user_id)
            )
        )

    def get_todos(self, user_id):
        user_todos = client.query(
            q.get(
                q.ref(self.collection, user_id)
            )
        )['data']['todos']
        todos = client.query(
            [
                q.get(q.ref(self.collection, todo_id))
            ] for todo_id in user_todos
        )
        return todos

    def update_todo(self, id, user_id, data):
        return client.query(
            q.update(
                q.ref(self.collection, user_id),
                {'data': data}
            )
        )['data']

    def delete_todo(self, user_id):
        data = client.query(
            q.delete(
                q.ref(self.collection, user_id)
            )
        )
        return data['data']

    def __repr__(self) -> str:
        f''