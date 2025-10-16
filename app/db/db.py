from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.auth.model.user import UserModel
from app.drone_details.model.drone_details import DroneDetailsModel
from app.equipment_details.model.equipement_services import EquipmentHistoryModel
from app.experience_record.model.experience_record import OperatorRecordModel
from app.industry.model.industry import SubIndustryModel, IndustryModel
from app.license.model.license import OperatorLicenseModel
from app.services.drone_services.model.drone_service import DroneServiceModel
from app.user.customer.model.customer import CustomerInfoModel, CustomerDetailsInfoModel, CustomerServicesDetailsModel
from app.user.operator.model.operator import OperatorInfoModel
import os

# MONGO_DETAILS = "mongodb://localhost:27017/prasad"


load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_URI")

async def init_db():
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_DETAILS)
    database: AsyncIOMotorDatabase = client.get_database()

    # Beanie init
    await init_beanie(
        database=database,
        document_models=[
            UserModel,
            CustomerInfoModel,
            OperatorInfoModel,
            DroneDetailsModel,
            EquipmentHistoryModel,
            OperatorLicenseModel,
            OperatorRecordModel,
            CustomerDetailsInfoModel,
            CustomerServicesDetailsModel,
            DroneServiceModel,
            IndustryModel,
            SubIndustryModel,
        ],
    )


async def drop_user_collection():
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_DETAILS)
    database: AsyncIOMotorDatabase = client.get_database()
    await database.drop_collection("operator_info")
    await database.drop_collection("customer_info")
