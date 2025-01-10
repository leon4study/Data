from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import text
from sqlalchemy.engine import URL
import pandas as pd

class MySqlClient : 
    def __init__(
        self,
        server_name : str,
        database_name : str,
        username : str,
        password : str,
        port : int = 3306,
    ):
        
        self.host_name = server_name
        self.database_name = database_name
        self.username  = username
        self.password = password
        self.port = port

        # MySQL 연결 URL
        connection_url = URL.create(
            drivername = "mysql+mysqlconnector", # 또는 mysql+pymysql
            username = username,
            password = password,
            host= server_name,
            port= port,
            database= database_name
        )

        #SQLAlchemy 엔진 생성
        self.engine = create_engine(connection_url)

    def create_table(self, metadata : MetaData) -> None:
        metadata.create_all(self.engine)
    
    def drop_table(self, table :Table) -> None:
        with self.engine.connect() as connection:
            connection.execute(text(f"DROP TABLE IF EXISTS {table.name}"))
    
    def insert(self, df: pd.DataFrame, table : Table, metadata : MetaData) -> None:
        
        self.create_table(metadata=metadata)
        df.to_sql(name=table.name, con = self.engine, if_exists="append", index= False)
    
    def upsert(self, df:pd.DataFrame, table : Table, metadata : MetaData)->None:

        self.create_table(metadata=metadata)

        # 데이터프레임을 레코드(딕셔너리 목록)으로 변환
        data = df.to_dict(orient="records")

        key_columns = [
            pk_column.name for pk_column in table.primary_key.columns.values()
        ]

        key_values = [ tuple( row[pk] for pk in key_columns) for row in data]
        delete_values = ", ".join(
            [f"({', '.join(map(repr, values))})" for values in key_values]
        )

        with self.engine.connect() as connection :
            if key_values:
                delete_sql = f"""
                    DELETE FROM {self.database_name}.{table.name}
                    WHERE ({', '.join(key_columns)}) IN (
                        {delete_values}
                    )
                """