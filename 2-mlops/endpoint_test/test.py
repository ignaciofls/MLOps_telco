import requests
import json

# URL for the web service.
scoring_uri = 'http://3fa3a086-4ce7-49c1-a46d-39980cd87806.westeurope.azurecontainer.io/score' # for example http://55975098-0a4f-4fb8-a94e-eae9780a7ffd.westeurope.azurecontainer.io/score

# The set of data to score
data = {"data":
    [{'gender': 'Male', 'SeniorCitizen':0, 'Partner':0, 'Dependents':0, 'tenure':20, 'PhoneService':1, 'MultipleLines':1, 'InternetService':'Fiber optic', 'OnlineSecurity':'Yes', 'OnlineBackup':1, 'DeviceProtection':1, 'TechSupport':'Yes', 'StreamingTV':1, 'StreamingMovies':1, 'Contract': 'One year', 'PaperlessBilling':1, 'PaymentMethod':'Electronic check', 'MonthlyCharges':70, 'TotalCharges':900}]
    }
        
# Convert to JSON string.
input_data = json.dumps(data)

# Set the content type.
headers = {'Content-Type': 'application/json'}

# Make the request and display the response.
resp = requests.post(scoring_uri, input_data, headers=headers)
print(resp.text)
