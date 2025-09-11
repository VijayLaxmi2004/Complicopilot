import requests

url = "http://127.0.0.1:8000/api/v1/receipts"
files = {'file': open(r'backend\uploads\reciepts\test\reciept1.png', 'rb')}
response = requests.post(url, files=files)
print(response.status_code)
print(response.json())