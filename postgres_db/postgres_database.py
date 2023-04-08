import psycopg2 as pc2
from configparser import ConfigParser

from src.custom_functionality import message_boxes as msg


class Database:

    def __init__(self):
        self._config_file_path: str = "postgres_db/postgres_user.ini"
        self._config_section: str = "postgresql"
        self._connection = self._connect()
        print(type(self._connection))

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
            with self._connection.cursor as crs:
                crs.callproc("get_text_by_id", (text_id,))
                result = crs.fetchone()
                return result

        except (Exception, pc2.DatabaseError) as error:
            msg.error_message(repr(error))
            self._connection.rollback()

