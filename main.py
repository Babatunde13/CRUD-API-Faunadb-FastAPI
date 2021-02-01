from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Header, Query, Body
import models
from jose import jwt
# import bcrypt, os

from schema import *

load_dotenv()

app = FastAPI()
 
@app.post(
    '/users/create/', 
    response_model=UserOutputWithTodo, 
    description='This route is for creating user accounts',
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserInput):
    user.password = bcrypt.hashpw(user.password, bcrypt.gensalt())
    try:
        user = models.User().create_user(user.dict())
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    return user

@app.post(
    '/users/token/', 
    response_model=Token, 
    description='This route is for creating user accounts'
)
async def get_token(user: UserSignin):
    user_data = models.User().get_user_by_email(user.email)
    if user_data and bcrypt.checkpw(user.password, user_data['password']):
        token = jwt.encode({'user': user_data}, key=os.getenv('SECRET_KEY'))
        return token
    header = {'WWW-Authenticate': 'Basic'}
    raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
                detail='Invalid email or password',
                headers=header
            )

async def authorize(authorization: str):
    if not authorization or len(authorization.split(' ')) != 2 or\
         authorization.split(' ')[0] != 'Bearer':
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            detail='Token not passed'
        )
    token = authorization.split(' ')[1]
    return jwt.decode(token, key=os.getenv('SECRET_KEY'), algorithms=[ 'HS256'])

@app.post(
    '/users/todo/',
    response_model=TodoOutput, 
    status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo: Todo, 
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    todo = models.Todo().create_todo(user['id'], todo.dict())
    todo['creator'] = user
    return todo

@app.get(
    '/users/todo/{todo_id}', 
    response_model=TodoOutput
)
async def get_todo(
    todo_id: str= Field(..., description='Id of the todo'),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    todo = models.Todo().get_todo(todo_id)
    if todo['user_id'] != user['id']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo.update({"creator": user})
    return  todo

@app.get(
    '/users/todos/', 
    response_model= UserOutputWithTodo,
    description='Get all Todos'
)

async def get_all_todos(
    date: Optional[str]=Query(
                            None, 
                            description='Date created'
                        ),
    name: Optional[str]=Query(
                            None, 
                            description='Some part of the name'
                        ),
    complete: Optional[bool]=Query(
                                None, 
                                description='Is the tod completed or not'
                            ),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; '\
                        'where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    # get all todo
    todos = models.Todo().get_todos(user['id'])
    # add user data
    user.update({'todos': todos})
    return todos

@app.put(
    '/users/todo/{todo_id}', 
    response_model=TodoOutput
)
async def update_todo(
    todo_id: str =Field(..., description='Id of the todo'),
    data: Todo = Body(...),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    todo = models.Todo().get_todo(todo_id)
    if todo['user_id'] != user['id']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = models.Todo().update_todo(todo_id, data)
    todo.update({"creator": user})
    return  todo

@app.delete(
    '/users/todo/{todo_id}', 
    response_model=TodoOutput
)
async def delete_todo(
    todo_id: str = Field(..., description='Id of the todo'),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    todo = models.Todo().get_todo(todo_id)
    if todo['user_id'] != user['id']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = models.Todo().delete_todo(todo_id)
    todo.update({"creator": user})
    return  todo