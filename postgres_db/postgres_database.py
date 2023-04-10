import psycopg2 as pc2
from configparser import ConfigParser
from datetime import datetime

from src.custom_functionality import message_boxes as msg


class Database:

    def __init__(self):
        self._config_file_path: str = "postgres_db/postgres_user.ini"
        self._config_section: str = "postgresql"
        self._connection = self._connect()

    def _connect(self):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(self._config_file_path)

        # get section, default to postgresql
        config_data = dict()

        params = parser.items(self._config_section)
        for param in params:
            config_data[param[0]] = param[1]

        try:
            return pc2.connect(**config_data)

        except (Exception, pc2.DatabaseError) as error:
            raise ValueError(error)

    def get_text_by_id(self, text_id: int):
        try:
            with self._connection.cursor() as crs:
                crs.callproc("get_text_by_id", (text_id,))
                result = crs.fetchone()
                return result

        except (Exception, pc2.DatabaseError) as error:
            msg.error_message(repr(error))
            self._connection.rollback()

#   	recieved_text_author varchar,
#	recieved_text_title varchar,
#	recieved_text_language varchar,
#	recieved_text_subject varchar,
#	recieved_l_date date,
#	recieved_r_date date,
#	texts_limit int

    def get_texts(
        self, 
        text_author: str,
        text_title: str,
        text_languages: str,
        text_subject: str,
        l_date: datetime,
        r_date: datetime,
        lim: str
    ):
        try:
            with self._connection.cursor() as crs:
                crs.callproc(
                    "get_texts",
                    (
                        text_author,
                        text_title,
                        text_languages,
                        text_subject,
                        l_date,
                        r_date,
                        lim
                    )
                )

                result = crs.fetchall()
                return result


        except (Exception, pc2.DatabaseError) as error:
            msg.error_message(repr(error))
            self._connection.rollback()
        
