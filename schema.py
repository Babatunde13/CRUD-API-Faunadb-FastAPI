'''Schmea of all data received and sent back to the user'''

from pydantic import BaseModel, Field
from typing import Optional, List

class DeletedData(BaseModel):
    message: str

class User(BaseModel):
    '''
        Base User schema contains name and email
    '''
    email: str = Field(
         None, title="The email of the user", max_length=300
    )
    fullname: str = Field(
         None, title="The name of the user", max_length=300
    )
     
class Todo(BaseModel):
    '''
        Schema of data expected when creating a new todo. Contains nae and is_completed field
    '''
    name: str = Field(None, title='The name of the todo')
    is_completed: bool = Field(
        False, title='Determines if the todo is completed or not defaults to False'
    )

class UserInput(User):
    '''
        Schema of data expected when creating a new user. 
        Contains name, email and password
    '''
    password: str = Field(
         None, title="The password of the user", max_length=14, min_length=6
    )

class UserOutput(User):
    '''
        Schema of data returned when a new user is created. 
        Contains name, email and id
    '''
    id: str = Field(None, title='The unique id of the user', min_length=1)

class TodoWithId(Todo):
    '''Base schema of todo data returned when getting a todo data'''
    id: str

class UserOutputWithTodo(UserOutput):
    '''
        Schema of data expected when getting all todo or when getting user data. 
        Contains name, email, id and an array of todos
    '''
    todos: List[TodoWithId] = Field(
         [], title="The todos created by the user"
    )

class TodoOutput(TodoWithId):
    creator: UserOutput

class Token(BaseModel):
    token: str

class UserSignin(BaseModel):
    email: str = Field(
         None, title="The email of the user", max_length=300
    )
    password: str = Field(
         None, title="The password of the user", max_length=300
    )