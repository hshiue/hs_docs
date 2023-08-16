import requests
import prsvtoken
import json
import pprint

config = 'DA_Production_SMTP.ini'
token = prsvtoken.get_token(config)
print(token)

def get_api_results(accesstoken, url):
    headers = {
                'Preservica-Access-Token': accesstoken,
                'Content-Type': "application/json"
              }
    response = requests.request('GET', url, headers=headers)
    return response

# validator.py –pre-ingest-object-path /path/to/M1126

url = 'https://nypl.preservica.com/api/content/search-within?q={"q":"","fields":[{"name":"spec.specCollectionID","values":["M6141"]},{"name":"xip.document_type","values":["SO"]},{"name":"xip.security_descriptor","values":[]}]}&parenthierarchy=e80315bc-42f5-44da-807f-446f78621c08&start=0&max=-1&metadata=xip.title,xip.document_type,xip.security_descriptor'

# url = 'https://nypl.preservica.com/api/entity/structural-objects/22938fc8-6ba9-425d-a7cd-167d46dbba3a/metadata/2c314ba4-24d0-47d9-bb9f-d6bdceab6288'

res = get_api_results(token, url)
json_obj = json.loads(res.text)
# print(json.dumps(json_obj, indent=1))
pprint.pprint(json_obj)

'''
M1126_ER_1 level:
  xip.title: M1126_ER_1
  xip.security_descripter: open

  https://nypl.preservica.com/api/content/search-within
'''