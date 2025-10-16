from fastapi import APIRouter, HTTPException,status
from typing import List
from app.auth.model.user import UserModel
from app.auth.schemas.user import UserResponse
from app.experience_record.model.experience_record import OperatorRecordModel
from app.experience_record.schemas.experience_record import OperatorRecordResponse
from app.license.model.license import OperatorLicenseModel
from app.license.schemas.license import LicenseResponse
from app.user.customer.model.customer import CustomerInfoModel, CustomerDetailsInfoModel, CustomerServicesDetailsModel
from app.user.customer.schemas.customer import CustomerInfoResponse, CustomerInfoDetailsResponse, \
    CustomerServicesDetailsResponse
from app.user.operator.model.operator import OperatorInfoModel
from app.user.operator.schemas.operator import OperatorInfoResponse

router = APIRouter(
    prefix="/user",
    tags=["User Management"],
)



@router.get("/all_user",response_model= List[UserResponse] ,status_code=status.HTTP_200_OK)
async def read_users():
    db_users = await UserModel.find_all().to_list()
    return db_users


# @router.get("/all_customer", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
# async def read_customers():
#     db_users = await UserModel.find((UserModel.role == "customer") or (UserModel.otp_status=="verified")).to_list()
#     return db_users or []


# @router.get("/all_drone_operator", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
# async def read_customers():
#     db_users = await UserModel.find((UserModel.role == "operator") or (UserModel.otp_status=="verified")).to_list()
#     return db_users or []




@router.get("/all_drone_operator",status_code=status.HTTP_200_OK)
async def get_all_operators():
    db_users = await UserModel.find(UserModel.role=="operator").to_list()
    response = []


    for db_user in db_users:
        user_res = UserResponse(**db_user.model_dump())
        db_operator_info = await OperatorInfoModel.find_one(OperatorInfoModel.user_id["id"] == db_user.id)
        db_operator_info_res= (
            OperatorInfoResponse(**db_operator_info.model_dump())
            if db_operator_info
            else None
        )
        db_operator_license=await OperatorLicenseModel.find_one(OperatorLicenseModel.user_id["id"]==db_user.id)
        db_operator_license_res=(
            LicenseResponse(**db_operator_license.model_dump())
            if db_operator_license
            else None
        )
        db_operator_record = await OperatorRecordModel.find_one(OperatorRecordModel.user_id["id"] == db_user.id)
        db_operator_record_res=(
            OperatorRecordResponse(**db_operator_record.model_dump())
            if db_operator_record
            else None
        )

        data={
            "operator":user_res,
            "operator_info":db_operator_info_res,
            "operator_license":db_operator_license_res,
            "operator_record":db_operator_record_res,
        }

        response.append(data)

    return response





@router.get("/all_customer", status_code=status.HTTP_200_OK)
async def get_all_customers():
    db_users = await UserModel.find(UserModel.role=="customer").to_list()
    response = []

    for db_user in db_users:
        user_res = UserResponse(**db_user.model_dump())

        db_customer_info = await CustomerInfoModel.find_one(
            CustomerInfoModel.user_id["id"] == db_user.id
        )
        db_customer_info_res = (
            CustomerInfoResponse(**db_customer_info.model_dump())
            if db_customer_info
            else None
        )

        db_customer_info_details = await CustomerDetailsInfoModel.find_one(
            CustomerDetailsInfoModel.user_id["id"] == db_user.id
        )
        db_customer_info_details_res = (
            CustomerInfoDetailsResponse(**db_customer_info_details.model_dump())
            if db_customer_info_details
            else None
        )

        db_customer_services = await CustomerServicesDetailsModel.find_one(
            CustomerServicesDetailsModel.user_id["id"] == db_user.id
        )
        db_customer_services_res = (
            CustomerServicesDetailsResponse(**db_customer_services.model_dump())
            if db_customer_services
            else None
        )

        customer_data = {
            "customer": user_res,
            "customer_info": db_customer_info_res,
            "customer_details": db_customer_info_details_res,
            "customer_services": db_customer_services_res,
        }

        response.append(customer_data)

    return response



@router.post("/suspend/${user_id}", status_code=status.HTTP_200_OK)
async def reset_password(user_id:str):
    db_user = await UserModel.get(user_id)
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    if not db_user.otp_status == "verified":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Your account is not active or has expired")
    db_user.account_status = "suspended"
    await db_user.save()
    return {"message":"you have suspended successfully"}



@router.get("/operator/{user_id}",status_code=status.HTTP_200_OK)
async def get_all_operators_by_id(user_id:str):
    db_user= await UserModel.find_one(UserModel.id==user_id)
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not db_user.role == "operator":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not operator")



    user_res = UserResponse(**db_user.model_dump())
    db_operator_info = await OperatorInfoModel.find_one(OperatorInfoModel.user_id["id"] == db_user.id)
    db_operator_info_res= (
        OperatorInfoResponse(**db_operator_info.model_dump())
        if db_operator_info
        else None
    )
    db_operator_license=await OperatorLicenseModel.find_one(OperatorLicenseModel.user_id["id"]==db_user.id)
    db_operator_license_res=(
        LicenseResponse(**db_operator_license.model_dump())
        if db_operator_license
        else None
    )
    db_operator_record = await OperatorRecordModel.find_one(OperatorRecordModel.user_id["id"] == db_user.id)
    db_operator_record_res=(
        OperatorRecordResponse(**db_operator_record.model_dump())
        if db_operator_record
        else None
    )

    data={
        "operator":user_res,
        "operator_info":db_operator_info_res,
        "operator_license":db_operator_license_res,
        "operator_record":db_operator_record_res,
    }



    return data

