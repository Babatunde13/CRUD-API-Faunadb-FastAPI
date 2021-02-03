from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Header, Query, Body
import models
import bcrypt, os, jwt

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
    user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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
    if user_data and bcrypt.checkpw(
                    user.password.encode('utf-8'), 
                    user_data['password'].encode('utf-8')
                ):
        token = jwt.encode({'user': user_data}, key=os.getenv('SECRET_KEY'))
        return {
            'token': token
        }
    header = {'WWW-Authenticate': 'Basic'}
    raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
                detail='Invalid email or password',
                headers=header
            )
 
async def authorize(authorization: str):
    if not authorization:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            detail='Token not passed'
        )
    if len(authorization.split(' ')) != 2 or\
         authorization.split(' ')[0] != 'Bearer':
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid Token'
        )
    token = authorization.split(' ')[1]
    return jwt.decode(token, key=os.getenv('SECRET_KEY'), algorithms=[ 'HS256'])['user']

@app.post(
    '/users/todos/',
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
    try:
        todo = models.Todo().create_todo(user['id'], todo.dict())
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    todo['creator'] = user
    return todo

@app.get(
    '/users/todos/{todo_id}', 
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
    try:
        todo = models.Todo().get_todo(todo_id) 
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    if not todo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No todo with that id')
    todo = todo['data']
    if todo and todo['user_id'] != user['id']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo.update({"creator": user})
    return  todo

@app.get(
    '/users/todos/', 
    response_model= UserOutputWithTodo,
    description='Get all Todos'
)

async def get_all_todos( 
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; '\
                        'where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    # get all todo
    try:
        todos = models.Todo().get_todos(user['id'])
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
    # add user data
    todos = [] if not todos else todos
    user.update({'todos': todos})
    return user

@app.put(
    '/users/todos/{todo_id}', 
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
    try:
        todo = models.Todo().get_todo(todo_id )
        if todo['data']['user_id'] != user['id']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        todo = models.Todo().update_todo(todo['ref'].id(), data.dict())
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    todo.update({"creator": user})
    return  todo

@app.delete(
    '/users/todos/{todo_id}', 
    response_model=DeletedData
)
async def delete_todo(
    todo_id: str = Field(..., description='Id of the todo'),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    user = await authorize(Authorization)
    try:
        todo = models.Todo().get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No todo with that id')
            
        if todo['data']['user_id'] != user['id']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        todo = models.Todo().delete_todo(todo['ref'].value['id'])
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    return  {'message': 'Todo Deleted successfully'}