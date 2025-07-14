#simple class to communicate with nucore

# Method 1: Using requests (recommended)
import requests
import json
import re

default_base_url="http://localhost:8080"
default_username="admin"
default_password="admin"

class nucoreAPI:
    def __init__(self, base_url:str=None, username:str=None, password:str=None):
        self.base_url=base_url if base_url else default_base_url
        self.username=username if username else default_username
        self.password=password if password else default_password

    def __get(self, path:str):
        try:
            url=f"{self.base_url}/{path}"
            # Method 1a: Using auth parameter (simplest)
            response = requests.get(
            url,
            auth=(self.username, self.password)
            )
            if response.status_code != 200:
                print (f"invalid url status code = {response.status_code}")
                return None
            return response
        except Exception as ex:
            print (f"failed connection {ex}")
            return None
    
    def __post(self, path:str, body:str, headers):
        try:
            url=f"{self.base_url}{path}"
            response = requests.post(url, auth=(self.username, self.password), data=body, headers=headers,  verify=False)
            if response.status_code != 200:
                print (f"invalid url status code = {response.status_code}")
                return None
            return response
        except Exception as ex:
            print (f"failed post: {ex}")
            return None

    def get_profiles(self):
        response = self.__get("/rest/profiles")
        if response == None:
            return None
        return response.json()
        #return json.dumps(response.json(), indent=2)

    def get_nodes(self):
        response = self.__get("/rest/nodes")
        if response == None:
            return None
        return response.text

    
    def get_d2d_key(self):
        """
        Sends a SOAP request for GetAllD2D, prints the full response, and returns the key value.

        Returns:
            str: The key value from the response (e.g., '07FF2D.BBC3F1'), or None if not found.

        Raises:
            requests.RequestException: If the SOAP request fails.
        """
        # SOAP request envelope (exact match to your provided envelope)
        soap_request = '''<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
            <s:Body>
                <u:GetAllD2D xmlns:u="urn:udi-com:service:X_IoX_Service:1"></u:GetAllD2D>
            </s:Body>
        </s:Envelope>'''

        # Headers matching the provided SOAP request
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPACTION': 'urn:udi-com:service:X_IoX_Service:1#GetAllD2D',  # Exact match
            'Connection': 'close'
        #    'Host': '192.168.0.105:8443'
        }

        # Add Authorization header if provided
        #if authorization:
        #    headers['Authorization'] = authorization

        try:

            # Send the SOAP request
            response = self.__post('/services', body=soap_request, headers=headers)

            xml_response = response.text

            # Print the full XML response
            #print("Full SOAP Response:")
            #print(xml_response)
            #print("-" * 50)  # Separator for readability

            # Extract the key using regex since XML is malformed
            key_match = re.search(r'<key>(.*?)</key>', xml_response)
            if key_match:
                return key_match.group(1)  # Return the key value, e.g., '07FF2D.BBC3F1'
            else:
                return None  # Key not found in response

        except requests.RequestException as e:
            raise Exception(f"SOAP request failed: {str(e)}")

    def upload_programs(self, programs:dict):
        if not programs:
            return False
        key=self.get_d2d_key()
        if not key:
            print ("couldn't get d2d key")
            return False
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'Connection': 'close'
        }

        for program_file_name, program_content in programs.items():
            try:
                self.__post(f'/program/upload/{program_file_name}?key={key}', body=program_content, headers=headers)
            except Exception as ex:
                print (ex)
                return False
        return True

# Example usage
if __name__ == "__main__":
    nucore=nucoreAPI()
    key = nucore.get_d2d_key()
    print (key)
