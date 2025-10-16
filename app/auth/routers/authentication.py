from fastapi import APIRouter, HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.auth.model.user import UserModel
from app.auth.schemas.otp_verify import UserOTPVerify
from app.auth.schemas.user import UserCreate,UserResponse
from app.utils.get_hashed_password import get_hashed_password,verify_password
from app.utils.otp_generate import generate_otp
from app.utils.email_config import send_otp, SendOtpModel
from app.utils.token_generation import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)



@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    hashed_password = get_hashed_password(user.password)
    db_user = await UserModel.find_one(UserModel.email == user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")
    otp=generate_otp()
    new_user = UserModel(
        email=user.email,
        password=hashed_password,
        account_status="pending",
        role=user.role,
        otp_status="pending",
        otp=otp
    )
    await new_user.insert()
    send_otp_data = SendOtpModel(email=new_user.email, otp=new_user.otp)
    await send_otp(send_otp_data)
    return {
        "message": "User registered successfully.Please check your email.A 6 digit otp has been sent.",
        "data":new_user
    }







@router.post("/otp_verify", status_code=status.HTTP_200_OK)
async def verify_otp(user:UserOTPVerify):
    db_user =await UserModel.find_one(UserModel.email == user.email)
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if user.otp != db_user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Wrong OTP")

    db_user.otp_status="verified"
    await db_user.save()
    return {"message":"You have  verified","data":db_user}








@router.post("/login", status_code=status.HTTP_200_OK)

async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await UserModel.find_one(UserModel.email == form_data.username)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")

    if not db_user.otp_status == "verified":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your account is not active or has expired")

    if not db_user.account_status=="active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not verified, please wait for admin approval or contact your administrator")

    token = create_access_token(data={"sub": db_user.email, "role": db_user.role, "user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}





@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(email:str):
    db_user = await UserModel.find_one(UserModel.email == email)
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    otp=generate_otp()
    db_user.otp=otp
    await db_user.save()
    send_otp_data = SendOtpModel(email=db_user.email, otp=db_user.otp)
    await send_otp(send_otp_data)
    return {
        "message": "User registered successfully.Please check your email.A 6 digit otp has been sent.",
        "data":db_user
    }





@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(new_password:str,email:str):
    db_user = await UserModel.find_one(UserModel.email == email)
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    if not db_user.otp_status == "verified":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Your account is not active or has expired")

    hashed_password = get_hashed_password(new_password)
    db_user.password = hashed_password
    await db_user.save()
    return {"message":"you have reset password successfully"}





