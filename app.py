import sys
import os
import pymongo
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import HTMLResponse, Response
from starlette.responses import RedirectResponse
import pandas as pd

from NetworkSecurity.utils.main_utils.utils import load_object
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel
from dotenv import load_dotenv
import certifi

ca = certifi.where()


load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
# print(mongo_db_url)



client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from NetworkSecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from NetworkSecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/predict")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.get("/predict", response_class=HTMLResponse)
async def predict_form(request: Request):
    return templates.TemplateResponse("table.html", {"request": request, "table": None})

@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        input_df = df.drop(columns=["Result", "predicted_column"], errors="ignore")
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        y_pred = network_model.predict(input_df)
        df['predicted_column'] = y_pred
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        os.makedirs("prediction_output", exist_ok=True)
        df.to_csv('prediction_output/output.csv', index=False)
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="localhost",port=8000)
