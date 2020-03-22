import pandas as pd
from sklearn.externals import joblib
from azureml.core.model import Model

import json
import pickle
import numpy as np

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType


input_sample = pd.DataFrame(data=[{'gender': 'Male', 'SeniorCitizen':0, 'Partner':1, 'Dependents':1, 'tenure':20, 'PhoneService':1, 'MultipleLines':1, 'InternetService':'Fiber optic', 'OnlineSecurity':1, 'OnlineBackup':1, 'DeviceProtection':1, 'TechSupport':1, 'StreamingTV':1, 'StreamingMovies':1, 'Contract': 'One year', 'PaperlessBilling':1, 'PaymentMethod':'Electronic check', 'MonthlyCharges':70, 'TotalCharges':900}])
output_sample = np.array([0])


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = Model.get_model_path('Churn_model')
    model = joblib.load(model_path)


@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        result = model.predict(data)
        return json.dumps({"result": result.tolist()})
    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})