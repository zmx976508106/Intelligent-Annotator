from abc import abstractmethod
import psycopg2


class DB_Manager(object):
    table_name = None

    def __init__(self, dbname="annotator", user="annotator", password="annotator"):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._conn = None
        self._cur = None

    def _connect(self):
        """
        连接数据库
        :return: None
        """
        para = "dbname=" + self._dbname \
               + " user=" + self._user \
               + " password=" + self._password
        self._conn = psycopg2.connect(para)
        self._cur = self._conn.cursor()

    def _close_connection(self):
        """
        关闭数据库连接
        :return: None
        """
        self._cur.close()
        self._conn.close()

    def _commit(self):
        """
        commit
        :return: None
        """
        self._conn.commit()

    def _execute(self, *args, **kwargs):
        """
        执行操作
        :param args:
        :param kwargs:
        :return: None
        """
        self._cur.execute(*args, **kwargs)

    def _fetchone(self):
        """
        获取查询结果中的一条记录
        :return: 查询结果中的一条记录
        """
        return self._cur.fetchone()

    def _fetchall(self):
        """
        获取查询结果中的所有记录
        :return: 查询结果中的所有记录
        """
        return self._cur.fetchall()

    @abstractmethod
    def create(self):
        """
        创建数据表
        :return: None
        """
        pass

    @abstractmethod
    def insert(self):
        """
        向数据表中插入记录
        :return: None
        """
        pass

    def delete(self, condition=''):
        """
        删除满足条件的记录
        :param condition: 删除条件
        :return: None
        """
        self._connect()
        sql = "DELETE FROM " + self.table_name
        sql = sql + " WHERE " + condition + ";" if not condition == '' else sql + ";"
        self._execute(sql)
        self._commit()
        self._close_connection()

    def update(self, ret, condition):
        """
        更新数据库记录
        :param ret: 更新结果
        :param condition: 更新条件
        :return: None
        """
        self._connect()
        sql = "UPDATE " + self.table_name + " SET " + ret + " WHERE " + condition + ";"
        self._execute(sql)
        self._commit()
        self._close_connection()

    def select(self, condition='', num=-1):
        """
        选择满足条件的记录
        :param condition: 选择条件
        :param num: 返回数量
        :return: 一定数量的选择结果
        """
        self._connect()
        sql = "SELECT * FROM " + self.table_name
        sql = sql + " WHERE " + condition + ";" if not condition == '' else sql + ";"
        self._execute(sql)
        self._commit()
        ret = self._fetchall()
        self._close_connection()
        return ret if num == -1 else ret[:num - 1]

    def drop(self):
        """
        删除数据表
        :return: None
        """
        self._connect()
        sql = 'DROP TABLE IF EXISTS ' + self.table_name + ';'
        self._cur.execute(sql)
        self._commit()
        self._close_connection()


class Labeled_DB_Manager(DB_Manager):
    table_name = "labeled_data"

    labeled_id = "labeled_id"
    unlabeled_id = "unlabeled_id"
    data_content = "data_content"
    labeled_time = "labeled_time"
    entity1 = "entity1"
    entity2 = "entity2"
    predicted_relation = "predicted_relation"
    labeled_relation = "labeled_relation"

    def create(self):
        """
        创建已标注数据表
        :return: None
        """
        self._connect()
        sql = "CREATE TABLE " + self.table_name + " ( \
                        labeled_id serial PRIMARY KEY, \
                        unlabeled_id int NOT NULL, \
                        data_content text NOT NULL, \
                        labeled_time timestamp NOT NULL, \
                        entity1 text, \
                        entity2 text, \
                        predicted_relation text, \
                        labeled_relation text);"
        self._cur.execute(sql)
        self._commit()
        self._close_connection()

    def insert(self, unlabeled_id=-1, data_content='', labeled_time='',
               entity1='', entity2='', predicted_relation='',
               labeled_relation=''):
        """
        向已标注数据表中插入记录
        :param unlabeled_id: 数据的 id
        :param data_content: 数据内容
        :param labeled_time: 标注时间
        :param entity1: 实体一
        :param entity2: 实体二
        :param predicted_relation: 预测关系
        :param labeled_relation: 标注关系
        :return: None
        """
        self._connect()
        sql = "INSERT INTO " + self.table_name + " ( \
                         unlabeled_id, data_content, labeled_time, \
                         entity1, entity2, predicted_relation, \
                         labeled_relation) \
                         VALUES (%s, %s, %s, %s, %s, %s, %s);"
        self._cur.execute(sql, (unlabeled_id, data_content, labeled_time,
                                entity1, entity2, predicted_relation,
                                labeled_relation))
        self._commit()
        self._close_connection()


class Unlabeled_DB_Manager(DB_Manager):
    table_name = "unlabeled_data"

    unlabeled_id = "unlabeled_id"
    data_content = "data_content"
    upload_time = "upload_time"

    def create(self):
        """
        创建未标注数据表
        :return: None
        """
        self._connect()
        sql = "CREATE TABLE " + self.table_name + " ( \
                        unlabeled_id serial PRIMARY KEY, \
                        data_content text NOT NULL, \
                        upload_time timestamp NOT NULL);"
        self._execute(sql)
        self._commit()
        self._close_connection()

    def insert(self, data_content='', upload_time=''):
        """
        向未标注数据表中插入记录
        :param data_content: 数据内容
        :param upload_time: 上传时间
        :return: None
        """
        self._connect()
        sql = "INSERT INTO " + self.table_name + " ( \
                        data_content, upload_time) \
                        VALUES (%s, %s);"
        self._execute(sql, (data_content, upload_time))
        self._commit()
        self._close_connection()


def test_unlabeled_db():
    """
    未标注数据库 测试
    :return: None
    """
    db = Unlabeled_DB_Manager()

    # 创建数据表
    try:
        db.create()
    except psycopg2.ProgrammingError:
        print('数据库已存在')
    else:
        print('数据库创建成功')

    # 删除数据表中的所有记录
    db.delete()

    # 向数据表中添加两条记录
    db.insert(data_content='content', upload_time='2015-08-08')
    db.insert(data_content='特朗普', upload_time='2016-06-07')
    records = db.select()
    print(records)

    # 更新数据记录
    db.update(ret="data_content='test'", condition="data_content='content'")
    records = db.select(condition="data_content='test'")
    print(records)

    # 删除某条记录
    db.delete(condition="data_content='特朗普'")
    records = db.select(condition="data_content='特朗普'")
    print(records)


def test_labeled_db():
    """
    已标注数据库 测试
    :return: None
    """
    db = Labeled_DB_Manager()

    # 创建数据表
    try:
        db.create()
    except psycopg2.ProgrammingError:
        print('数据库已存在')
    else:
        print('数据库创建成功')

    # 删除数据表中的所有记录
    db.delete()

    # 向数据表中添加两条记录
    db.insert(unlabeled_id=1, data_content="特朗普是奥巴马的儿子", labeled_time="2016-01-01", entity1="奥巴马",
              entity2="特朗普", predicted_relation="儿子", labeled_relation="爸爸")
    db.insert(unlabeled_id=2, data_content="金正恩又名金三胖", labeled_time="2014-06-06", entity1="金正恩",
              entity2="金三胖", predicted_relation="又名", labeled_relation="又名")
    records = db.select()
    print(records)

    # 更新数据表记录
    db.update(ret="labeled_time='1970-01-01', entity1='不是奥巴马'", condition="unlabeled_id=1")
    records = db.select()
    print(records)

    # 删除数据表记录
    db.delete(condition="entity1='奥巴马' OR entity1='金正恩'")
    records = db.select()
    print(records)


if __name__ == '__main__':
    test_unlabeled_db()
    print()
    test_labeled_db()