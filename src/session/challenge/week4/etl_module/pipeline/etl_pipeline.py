import os
from dotenv import load_dotenv
from etl_module.connectors.weather_api import WeatherApiClient
from etl_module.connectors.mysql import MySqlClient
from etl_module.assets.weather import extract_weather, transform_weather, load_weather


def main():
    """
    main 함수는 전체 ETL 프로세스를 실행합니다.

    1. 환경 변수를 로드하여 Weather API와 MySQL 데이터베이스 연결에 필요한 정보를 가져옵니다.
    2. WeatherApiClient와 MySqlClient 객체를 생성합니다.
    3. ETL 프로세스를 순차적으로 수행합니다:
        - 데이터를 Weather API에서 추출합니다.
        - 추출된 데이터를 변환하여 필요한 형태로 가공합니다.
        - 가공된 데이터를 MySQL 데이터베이스에 적재합니다.
    """
    print('ETL 시작')

    load_dotenv()
    API_KEY = os.environ.get("API_KEY")
    DB_SERVER_HOST = os.environ.get("DB_SERVER_HOST")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    DB_PORT = os.environ.get("DB_PORT")

    weather_api_client = WeatherApiClient(api_key=API_KEY)
    my_sql_client = MySqlClient(
        server_name=DB_SERVER_HOST,
        database_name=DB_DATABASE,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        port=DB_PORT,
    )

    # ETL 실행
    print('E 시작')
    df = extract_weather(weather_api_client=weather_api_client)
    print('E 시작')

    print('E 시작')
    clean_df = transform_weather(df)
    print('E 시작')

    print('E 시작')
    print(clean_df.shape)
    load_weather(df=clean_df, my_sql_client=my_sql_client)
    print('E 시작')


if __name__ == "__main__":
    main()
