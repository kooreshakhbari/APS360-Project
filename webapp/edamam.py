import requests
import pprint
import json
# Set up the parameters we want to pass to the API.
# q: any ingredient
# app_id is the application ID of recipe search 
# app_key is the application authentication key
parameters = {"q": 'apple, butter', "app_id": '85b9158f', "app_key": 'b6e60f224ffd3c0a1d048088ada1dc22'}
# Make a get request with the parameters.
response = requests.get("https://api.edamam.com/search", params=parameters)

# If status code is 200, the request is successful
print('Status Code:', response.status_code)

# Get the response data as a python object.
data = response.json()

for hit in data['hits']:
    print(hit['recipe']['label'])

# pprint.pprint(data)



# print(response.content["label"])