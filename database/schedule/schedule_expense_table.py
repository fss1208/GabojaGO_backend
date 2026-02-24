from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleExpenseModel

class ScheduleExpenseTable(BaseTable):

    NAME = "schedule_expense"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleExpenseModel:
        return ScheduleExpenseModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iUserFK=row[2],
            dtExpense=row[3],
            chCategory=row[4],
            nMoney=row[5],
            iLocation=row[6],
            strMemo=row[7]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuples: tuple) -> list[ScheduleExpenseModel]:
        return [ScheduleExpenseTable.TO_MODEL(row) for row in rows_tuples]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleExpenseTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iUserFK INT NOT NULL,
                dtExpense DATETIME NOT NULL,
                chCategory CHAR(1) NOT NULL,                    -- T:교통, L:숙박, F:식비, E:기타
                nMoney INT NOT NULL,
                iLocation INT DEFAULT 0,                        -- 없는 경우 : 0
                strMemo VARCHAR(1024),
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(sem: ScheduleExpenseModel) -> str:
        return f"SELECT * FROM {ScheduleExpenseTable.NAME} WHERE iPK={sem.iPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"SELECT * FROM {ScheduleExpenseTable.NAME} WHERE iScheduleFK={iScheduleFK} ORDER BY dtExpense"

    @staticmethod
    def TO_INSERT_QUERY(sem: ScheduleExpenseModel) -> str:
        return f"INSERT INTO {ScheduleExpenseTable.NAME} (iScheduleFK,iUserFK,dtExpense,chCategory,nMoney,iLocation,strMemo) " + \
            f"VALUES ({sem.iScheduleFK},{sem.iUserFK},'{sem.dtExpense}','{sem.chCategory}',{sem.nMoney},{sem.iLocation},'{sem.strMemo}')"

    @staticmethod
    def TO_UPDATE_QUERY(sem: ScheduleExpenseModel) -> str:
        return f"UPDATE {ScheduleExpenseTable.NAME} " + \
               f"SET dtExpense='{sem.dtExpense}',chCategory='{sem.chCategory}',nMoney={sem.nMoney},iLocation={sem.iLocation},strMemo='{sem.strMemo}' " + \
               f"WHERE iPK={sem.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(sem: ScheduleExpenseModel) -> str:
        return f"DELETE FROM {ScheduleExpenseTable.NAME} WHERE iPK={sem.iPK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ScheduleExpenseTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleExpenseTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
