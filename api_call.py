import requests
import json

def gate_pass_data():
    api_url = "http://localhost:8000/api/api/gatepasses/"

    response = requests.get(api_url)

    response.json()

    status_code = response.status_code

    if status_code == 200:
        data = response.json()  # Assuming the response is JSON
        # print(data)
    else:
        print("Request failed with status code:", response.status_code)
        
    return data


def post_entry(data):
    
    url = "http://localhost:8000/api/api/class-entries/"
    headers = {

         "Content-Type": "application/json", 
    }
    
    
    # data = {
    #     "user": 1,
    #     "gatepass": 1,
    #     "time_in": "2024-11-18",  # Date format: YYYY-MM-DD
    #     "time_out": "12:32:00",   # Time format: HH:MM:SS
    #     "date": "2024-11-07"       # Date format: YYYY-MM-DD
    # }
    
    json_data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=json_data)
    
       # Check the response status
    if response.status_code == 201:
        print("Success! Class entry created:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
        
# post_entry()


def post_face_detect_flag(data):
    
    url = "http://localhost:8000/api/api/face_detect_flag/"
    headers = {

         "Content-Type": "application/json", 
    }
    
    
    # data = {
    #     "user": 1,
    #     "gatepass": 1,
    #     "time_in": "2024-11-18",  # Date format: YYYY-MM-DD
    #     "time_out": "12:32:00",   # Time format: HH:MM:SS
    #     "date": "2024-11-07"       # Date format: YYYY-MM-DD
    # }
    
    json_data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=json_data)
    
       # Check the response status
    if response.status_code == 201:
        print("Success! Class entry created:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
        
    
# data = {"flag":0}
        
# post_face_detect_flag(data)



def post_real_t_match(data):
    
    url = "http://localhost:8000/api/api/realtime_match/"
    headers = {

         "Content-Type": "application/json", 
    }
    
    
    # data = {
    #     "user": 1,
    #     "gatepass": 1,
    #     "time_in": "2024-11-18",  # Date format: YYYY-MM-DD
    #     "time_out": "12:32:00",   # Time format: HH:MM:SS
    #     "date": "2024-11-07"       # Date format: YYYY-MM-DD
    # }
    
    json_data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=json_data)
    
       # Check the response status
    if response.status_code == 201:
        print("Success! match percentage posted created:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
        
    
    

