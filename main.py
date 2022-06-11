from logging import exception
from plistlib import UID
from fastapi import FastAPI
from fastapi import HTTPException, Request, status, Depends
from sqlalchemy.orm import Session
import db, schema
from typing import List

db.Base.metadata.create_all(bind = db.engine)

app = FastAPI()

@app.post("/users/create", status_code= status.HTTP_201_CREATED, response_model= schema.userInput)
def create(user: schema.userInput, dbd: Session = Depends(db.get_db)):
    user_email = dbd.query(db.User).filter(db.User.email == user.email).first()

    if not user_email:
        user_dict = user.dict()
        new_user = db.User(**user_dict)
        dbd.add(new_user)
        dbd.commit()
        dbd.refresh(new_user)
    else:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN, detail = f'Email already exists'
        )
    return new_user

@app.get("/users/{uid}", status_code= status.HTTP_201_CREATED, response_model= schema.userOut)
def create(uid: int, dbd: Session = Depends(db.get_db)):
    user_uid = dbd.query(db.User).filter(db.User.uid == uid).first()

    if not user_uid:
    
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND, detail = f'user not found'
        )
    return user_uid

@app.get('/users', response_model= List[schema.userOut])
def get_all(dbd: Session = Depends(db.get_db)):
    data = dbd.query(db.User).all()
    return data

@app.delete('/users/delete/{uid}', status_code= status.HTTP_204_NO_CONTENT)
def delete_user(uid: int, dbd: Session = Depends(db.get_db)):
    post = dbd.query(db.User).filter(db.User.uid == uid)

    if post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f'user with id: {uid} not found')
        
    post.delete(synchronize_session = False)
    dbd.commit()

@app.put('/users/update/{uid}', status_code= status.HTTP_201_CREATED, response_model= schema.userOut)
def update_user(uid: int, user: schema.userInput, dbd: Session = Depends(db.get_db)):
    data = dbd.query(db.User).filter(db.User.uid == uid)

    if data.first() == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'user with id: {uid} not found')
    print(user.dict())
    
    data.update(user.dict(), synchronize_session= False)
    dbd.commit()
    return data.first()


if __name__ == '__main__':
    app.run()