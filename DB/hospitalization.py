from mysql.connector import connect as my_connect, Error as my_error, errorcode
from logging import error


class HDB:
    """
    Hospitalization Database connection service
    """

    def __init__(self, **kwargs):
        """
        Создаёт экземпляр класса с указанными параметрами. Если параметры не указаны, то используются следующие:
        username: str = "root",
        password: str = "",
        host: str = "localhost",
        port: int = 3306,
        database: str = "gosp"
        """
        props = kwargs.keys()
        self._port = kwargs.get("port") if "port" in props else "3306"
        self._host = kwargs.get("host") if "host" in props else "localhost"
        self._username = kwargs.get("username") if "username" in props else "root"
        self._password = kwargs.get("password") if "password" in props else ""
        self._database = kwargs.get("database") if "database" in props else "gosp"

        try:
            self._connection = my_connect(host=self._host,
                                          port=self._port,
                                          user=self._username,
                                          password=self._password,
                                          database=self._database,
                                          autocommit=True)
            if self._connection:
                # self._connection.config(autocommit=True)
                self._cursor = self._connection.cursor()
        except my_error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def __del__(self):
        """
        Страховка для корректного закрытия соединения с БД
        """
        self._cursor.close()
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __repr__(self):
        return "Соединение с БД Госпитализация выполненно" if self._connection \
            else "Соединение с БД Госпитализация не выполненно"

    def find_patient(self, fio: str, birth_year: int, region: str, phone: str) -> int:
        """
        Ищет запись госпитализации для пациента.
        :param fio: ФИО
        :param birth_year: год рождения
        :param region: регион проживания
        :param phone: номер телефона
        :return: patient_id: int: ID пациента в БД Госпитализация
        """
        stmt = "SELECT p.id FROM gosp.patient as p " \
               "left join gosp.regions as r on p.region_id=r.id left join gosp.phone_numbers as ph on p.id = ph.pid" \
               " WHERE p.fname=%(fname)s and p.sname=%(sname)s " \
               "and p.patronymic=%(patronymic)s and p.bth_year=%(bth_year)s and r.name LIKE %(region)s " \
               "and ph.phone=%(phone)s;"

        fio_lst = fio.strip().upper().split()
        region_prop = f"%{region.replace(' ', '%')}%"
        stmt_props = {
            'fname': fio_lst[0],
            'sname': fio_lst[1],
            'patronymic': fio_lst[2],
            'bth_year': birth_year,
            'region': region_prop,
            'phone': f"8{phone[-10:len(phone)]}"
        }
        result = {}
        try:
            self._cursor.execute(stmt, stmt_props)
            result = self._cursor.fetchall()
        except my_error as err:
            error(err.msg)

        return result[0][0] if result else {}

    def find_patient_by_tg_user_id(self, tg_id: int) -> dict:
        """
        Ищет пациента по tg_user_id
        :param tg_id: ИД пользователя в Телеграм
        :return: ИД пациента в БД Госпитализация
        """
        pid, fname, sname, patronymic = -1, '', '', ''
        stmt = "SELECT id, fname, sname, patronymic FROM gosp.patient WHERE tg_user_id=%s"
        try:
            self._cursor.execute(stmt, (tg_id,))
            pid, fname, sname, patronymic = self._cursor.fetchall()[0] or (-1, '', '', '')
        except my_error as err:
            error(err.msg)
        finally:
            return {"pid": pid, "fio": ' '.join((fname, sname, patronymic))}

    def find_patient_hospitalizations(self, pid: int) -> list:
        """
        Ищет запись госпитализации для пациента.
        :param pid: ID пациента в БД Госпитализация
        :return: dict: hosp_id: int: записи госпитализации, hosp_date: date: дата госпитализации,
                        hosp_accepted: bool: статус подтверждения записи или пустой список
        """
        stmt = "SELECT m.id, m.gosp_date, m.accepted FROM gosp.main as m " \
               " WHERE m.accepted=0 and m.pid=%(pid)s"

        hosp_list = []
        try:
            self._cursor.execute(stmt, {"pid": pid})
            hospitalization_tuples_list = self._cursor.fetchall()
            if len(hospitalization_tuples_list) > 0:
                hosp_list = [{"hosp_id": hosp_tuple[0],
                              "hosp_date": hosp_tuple[1],
                              "hosp_accepted": hosp_tuple[2]}
                             for hosp_tuple in hospitalization_tuples_list]
        except my_error as err:
            error(err.msg)

        return hosp_list

    def update_patient(self, pid: int, **kwargs):
        """
        Обновляет данные по пациенту
        :param pid: обязательный параметр ИД пациента в БД Госпитализация
        :param kwargs: словарь полей и их значений, которые надо поменять, должен соответствовать полям в БД
        """
        get_patient_columns_stmt = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'gosp' " \
                                   "AND TABLE_NAME = 'patient';"
        self._cursor.execute(get_patient_columns_stmt)
        patient_table_columns = [row[0] for row in self._cursor.fetchall()]
        wrong_column_names = set(kwargs.keys()) - set(patient_table_columns)
        if len(wrong_column_names) > 0:
            error(f"Переданы не существующие имена полей таблицы: {wrong_column_names}")
            return

        fields = [f"{key}=%({key})s" for key in kwargs.keys() if key != 'id']
        stmt = f"UPDATE patient SET {' '.join(fields)} WHERE id=%(id)s"
        kwargs.update({"id": pid})
        try:
            self._cursor.execute(stmt, kwargs)
        except my_error as err:
            error(err.msg, err.args, exc_info=err.errno)

    def update_hospitalization(self, hospitalization_id: int, accepted: bool):
        """
        Обновляет статус подтверждения записи госпитализации с указанным id
        :param hospitalization_id: id записи госпитализации
        :param accepted: значение статуса
        """
        stmt = "UPDATE gosp.main SET accepted=1 WHERE id=%s;"

        if accepted:
            try:
                self._cursor.execute(stmt, (hospitalization_id,))
            except my_error as err:
                error(err.msg)


if __name__ == '__main__':
    from settings import HOSP_DB, HOSP_HOST, HOSP_PASS, HOSP_PORT, HOSP_USER

    with HDB(username=HOSP_USER,
             password=HOSP_PASS,
             host=HOSP_HOST,
             port=HOSP_PORT,
             database=HOSP_DB) as hosp_db:
        hosp_db.update_patient(id=37647, tg_user_id=353380448)
