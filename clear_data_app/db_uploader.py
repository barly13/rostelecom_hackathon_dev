import os
import sys

from pandas import DataFrame
from sqlalchemy import create_engine, MetaData, text


class Uploader:
    DB_NAME = 'hackaton'
    DB_USER = 'postgres'
    DB_PASSWORD = '12345678'
    DB_HOST = 'localhost'
    DB_PORT = '5432'

    def __init__(self):
        self.__db_url = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        self.__engine = create_engine(self.__db_url)
        self.__dir_clear_csvs = '../cohort_analysis/clear_data\\'

    def upload_df_to_sql(self, df: DataFrame, table_name: str):
        try:
            df.to_sql(
                table_name,
                self.__engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            print(f"Таблица {table_name} успешно заполнена")
        except Exception as e:
            print(f"Ошибка при обработке {table_name}: {str(e)}")

    def clear_data_in_tables(self):
        metadata = MetaData()
        metadata.reflect(bind=self.__engine)

        with self.__engine.connect() as connection:
            # Отключаем проверку внешних ключей
            connection.execute(text('SET session_replication_role = replica;'))
            # TRUNCATE для каждой таблицы
            for table in reversed(metadata.sorted_tables):
                connection.execute(text(f'TRUNCATE TABLE {table.name} CASCADE;'))
            connection.commit()

            # Включаем проверку внешних ключей обратно
            connection.execute(text('SET session_replication_role = default;'))

    def save_data_in_dir(self, df: DataFrame, table_name: str):
        if not os.path.exists(self.__dir_clear_csvs):
            os.mkdir(self.__dir_clear_csvs)
        df.to_csv(f'{self.__dir_clear_csvs + table_name}.csv', index=False, encoding='utf-8')







