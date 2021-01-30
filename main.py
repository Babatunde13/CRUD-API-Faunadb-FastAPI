from fastapi import FastAPI, HTTPException, status, Header, Query
from models import *
from schema import *

app = FastAPI()

data = [
    {
        'id': 1,
        'fullname': 'Babatunde Koiki',
        'email': 'kkkkk',
        'token': '1',
        'password': 'nife'
    },
    {
        'id': 2,
        'name': 'Bbaa Koiki',
        'email': 'kkkaagkk'
    },
    {
        'id': 3,
        'name': 'Babatunde Ayo',
        'email': 'asd'
    },
    {
        'id': 4,
        'name': 'Ayo Aina',
        'email': 'aserg'
    },
    {
        'id': 5,
        'name': 'B Koiki',
        'email': 'kkkkk'
    },
    {
        'id': 6,
        'name': 'A Koiki',
        'email': 'kkkkk'
    }
]

@app.post(
    '/users/create/', 
    response_model=UserOutputWithTodo, 
    description='This route is for creating user accounts',
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserInput):
    print(user.fullname)
    return user

@app.post(
    '/users/token/', 
    response_model=Token, 
    description='This route is for creating user accounts'
)
async def get_token(user: UserSignin):
    header = {'WWW-Authenticate': 'Basic'}
    print(user.password)
    for u in data:
        if u['email'] == user.email:
            if u['password'] == user.password:
                return {'token': u['token']}
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
                detail='Invalid email or password',
                headers=header
            )
    raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
                detail='Invalid email or password',
                headers=header
            )

async def authorize(authorization):
    if not authorization:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            detail='Token not passed'
        )

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
    await authorize(Authorization)
    d=todo.dict()
    d.update({'creator': data[0]})
    d['id'] = 1
    return d

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
    await authorize(Authorization)
    # get todo based on id
    todo = {
        "name": "Go to market",
        'id':1
    }
    todo.update({"creator": data[0]})
    return  todo
    # pass

@app.get(
    '/users/todos/', 
    response_model= UserOutput,
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
    await authorize(Authorization)
    # get all todo
    # add user data
    # return  todo
    pass

@app.put(
    '/users/todo/{todo_id}', 
    response_model=TodoOutput
)
async def update_todo(
    todo_id: str =Field(..., description='Id of the todo'),
    Authorization: str= Header(
        None, 
        description='Authorization is in form of Bearer &lt;token&gt; where token is given in the /users/token/ endpoint'
    )
):
    await authorize(Authorization)
    # get todo based on id
    # update the todo
    # return  todo
    pass

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
    await authorize(Authorization)
    # get todo based on id
    # delete todo
    # return  todo
    pass 