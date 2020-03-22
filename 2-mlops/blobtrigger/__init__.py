import logging
import requests
import azure.functions as func

def main(myblob: func.InputStream):
        logging.info(f"Python blob trigger function processed blob \n"
                f"Name: {myblob.name}\n"
                f"Blob Size: {myblob.length} bytes")
        payload = "{\"definition\": {\r\n                \"drafts\": [],\r\n                \"id\": 18,\r\n                \"name\": \"MLops_demo\",\r\n                \"path\": \"\\\\\",\r\n                \"type\": \"build\",\r\n                \"queueStatus\": \"enabled\"\r\n                },\r\n\"buildNumber\": 1}"
#BuildID can be found in your devops pipeline. For example it is 18 in this url build: https://dev.azure.com/{organization}/{project}/_build?definitionId=18&_a=summary       
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic heregoesyourPAT'
            }            
        url = "https://dev.azure.com/{organization}/{project}/_apis/build/builds?api-version=5.1"
        response = requests.request("POST", url, headers=headers, data = payload)
        print(response.text.encode('utf8'))