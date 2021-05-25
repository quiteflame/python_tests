import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise
from passlib.hash import bcrypt
from models.db import *

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'api/token')
JWT_SECRET = 'n~2NAPpm?pCJNn2HL!)3'

register_tortoise(
    app, 
    db_url = 'sqlite://db.sqlite3',
    modules = {'models': ['models.db']},
    generate_schemas = True,
    add_exception_handlers = True
)

async def authenticate_user(username: str, password: str):
    user = await User.filter(username = username).first()

    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(jwt = token, key = JWT_SECRET, algorithms = ['HS256'])
        user = await User.filter(id = payload.get('id')).first()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    return await User_Pydantic.from_tortoise_orm(user)

@app.post("/api/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(username = form_data.username, password = form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(payload = user_obj.dict(), key = JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}

@app.post('/api/users', response_model = User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username = user.username, password_hash = bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.get('/api/users/me', response_model = User_Pydantic)
async def me(user: User_Pydantic = Depends(get_current_user)):
    return user