import requests

class WeatherApiClient:

    def __init__(self, api_key : str):
        self.base_url = 'http://api.openweathermap.org/data/2.5'
        if api_key is None:
            raise Exception("API 키 None")
        self.api_key = api_key

    def get_city(self, city_name : str, temperature_units : str = 'metric') -> dict:
        params  = {"q": city_name, "units": temperature_units, "appid":self.api_key}
        response = requests.get(f"{self.base_url}/weather", params= params)
        if response.status_code == 200:
            return response.json()
        else : 
            raise Exception(
                f"Open Weather API에서 데이터를 추출하지 못했습니다. 상태 코드 {response.status_code}.\n응답 : {response.text}"
            )