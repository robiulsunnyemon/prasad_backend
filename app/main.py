from fastapi import FastAPI
from app.db.db import init_db, drop_user_collection
from app.auth.routers.authentication import router as auth_router
from app.auth.user_management.user_management import router as user_router
from app.auth.profile.profile import router as profile_router
from app.user.customer.router.customer import router as customer_router
from app.user.operator.router.operator import router as operator_router
from app.drone_details.routers.drone_details import router as drone_details_router
from app.equipment_details.routers.equipment_services import router as equipement_router
from app.license.router.license import router as license_router
from app.experience_record.routers.experience_record import router as experience_record_router
from app.services.drone_services.router.drone_services import router as drone_services_router
from app.industry.router.industry import router as industry_router

app = FastAPI()


@app.on_event("startup")
async def startup():
    await  init_db()

@app.get("/",tags=["Root"])
async def root():
    return {"message": "Hello Prasad"}

@app.delete("/drop-collection",tags=["Drop Collection"])
async def drop_collection():
    await drop_user_collection()
    return {"message": "Collection dropped successfully"}


### routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(customer_router)
app.include_router(operator_router)
app.include_router(drone_details_router)
app.include_router(equipement_router)
app.include_router(license_router)
app.include_router(experience_record_router)
app.include_router(drone_services_router)
app.include_router(industry_router)