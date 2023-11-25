import os

from fastapi import FastAPI, File, UploadFile, Response
from pydantic import BaseModel
from typing import List
from utils import *
import pandas as pd
import numpy as np
import pickle
import re

with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/ohe.pkl', 'rb') as f:
    ohe = pickle.load(f)
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)


app = FastAPI()


class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


class Items(BaseModel):
    objects: List[Item]


@app.post("/predict_item")
def predict_item(item: Item) -> float:


    data = pd.DataFrame.from_dict(pd.json_normalize(item.dict()))
    data = process_data(data)
    cat_cols = data.select_dtypes(include=['object', 'category']).columns
    num_cols = data.select_dtypes(exclude=['object', 'category']).columns
    data_ohe = pd.DataFrame(ohe.transform(data[cat_cols]), columns=ohe.get_feature_names_out(cat_cols))
    data_scaled = pd.DataFrame(scaler.transform(data[num_cols]), columns=num_cols)
    final = pd.concat([data_scaled,data_ohe], axis=1)
    response = model.predict(final)
    return np.round(np.exp(response))


@app.post("/predict_items")
def predict_items(file: UploadFile = File(...)):
    data = pd.read_csv(file.file)
    df = data.copy()
    df = df.drop(columns=['selling_price'], axis=1)
    df = process_data(df)
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    num_cols = df.select_dtypes(exclude=['object', 'category']).columns
    data_ohe = pd.DataFrame(ohe.transform(df[cat_cols]), columns=ohe.get_feature_names_out(cat_cols))
    data_scaled = pd.DataFrame(scaler.transform(df[num_cols]), columns=num_cols)
    final = pd.concat([data_scaled,data_ohe],axis=1)
    predict = model.predict(final)
    data['predict'] = np.round(np.exp(predict))

    data.to_csv('predict.csv', index=False)
    with open('predict.csv', 'rb') as buffer:
        f = buffer.read()

    os.remove('predict.csv')

    headers = {'Content-Disposition': f'attachment; filename=predict.csv',
               'Content-Type': 'text/csv'}

    return Response(content=f, headers=headers)
