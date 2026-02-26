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
            nMoney=row[3],
            dtExpense=row[4],
            chCategory=row[5],
            strMemo=row[6]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleExpenseModel]:
        return [ScheduleExpenseTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleExpenseTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iUserFK INT NOT NULL,
                nMoney INT NOT NULL,
                dtExpense DATETIME NOT NULL,
                chCategory CHAR(1) NOT NULL,
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
        return f"INSERT INTO {ScheduleExpenseTable.NAME} (iScheduleFK,iUserFK,nMoney,dtExpense,chCategory,strMemo) " + \
               f"VALUES ({sem.iScheduleFK},{sem.iUserFK},{sem.nMoney},'{sem.dtExpense}','{sem.chCategory}','{sem.strMemo}')"

    @staticmethod
    def TO_UPDATE_QUERY(sem: ScheduleExpenseModel) -> str:
        return f"UPDATE {ScheduleExpenseTable.NAME} " + \
               f"SET nMoney={sem.nMoney},dtExpense='{sem.dtExpense}',chCategory='{sem.chCategory}',strMemo='{sem.strMemo}' " + \
               f"WHERE iPK={sem.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(iScheduleExpensePK: int) -> str:
        return f"DELETE FROM {ScheduleExpenseTable.NAME} WHERE iPK={iScheduleExpensePK}"

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
