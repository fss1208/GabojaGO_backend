from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleUserModel

class ScheduleUserTable(BaseTable):

    NAME = "schedule_user"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleUserModel:
        return ScheduleUserModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iUserFK=row[2],
            dtCreate=row[3]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuples: tuple) -> list[ScheduleUserModel]:
        return [ScheduleUserTable.TO_MODEL(row) for row in rows_tuples]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleUserTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iUserFK INT NOT NULL,
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(sum: ScheduleUserModel) -> str:
        return f"SELECT * FROM {ScheduleUserTable.NAME} WHERE iPK={sum.iPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"SELECT * FROM {ScheduleUserTable.NAME} WHERE iScheduleFK={iScheduleFK} ORDER BY dtCreate"

    @staticmethod
    def TO_SELECT_DUPLICATED_USER_QUERY(sum: ScheduleUserModel) -> str:
        return f"SELECT * FROM {ScheduleUserTable.NAME} WHERE iScheduleFK={sum.iScheduleFK} AND iUserFK={sum.iUserFK}"

    @staticmethod
    def TO_INSERT_QUERY(sum: ScheduleUserModel) -> str:
        return f"INSERT INTO {ScheduleUserTable.NAME} (iScheduleFK,iUserFK) " + \
            f"VALUES ({sum.iScheduleFK},{sum.iUserFK})"

    @staticmethod
    def TO_DELETE_QUERY(sum: ScheduleUserModel) -> str:
        return f"DELETE FROM {ScheduleUserTable.NAME} WHERE iPK={sum.iPK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ScheduleUserTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleUserTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
