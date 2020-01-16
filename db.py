#coding: utf-8

import sqlite3
import os

class Sql():
    __DB_FILE    = None
    __DB_CONN    = None
    __DB_TABLE   = ""
    __OPT_WHERE  = ""
    __OPT_LIMIT  = ""
    __OPT_ORDER  = ""
    __OPT_FIELD  = "*"
    __OPT_PARAM  = ()

    def __init__(self):
        self.__DB_FILE = 'data/default.db'

    def __GetConn(self):
        try:
            if self.__DB_CONN == None:
                self.__DB_CONN = sqlite3.connect(self.__DB_FILE)
        except Exception,ex:
            return "error: " + str(ex)

    def dbfile(self,name):
        self.__DB_FILE = 'data/' + name + '.db'
        return self

    def table(self,table):
        self.__DB_TABLE = table
        return self


    def where(self,where,param):
        if where:
            self.__OPT_WHERE = " WHERE " + where
            self.__OPT_PARAM = param
        return self


    def order(self,order):
        if len(order):
            self.__OPT_ORDER = " ORDER BY "+order
        return self


    def limit(self,limit):
        if len(limit):
            self.__OPT_LIMIT = " LIMIT "+limit
        return self


    def field(self,field):
        if len(field):
            self.__OPT_FIELD = field
        return self


    def select(self):
        self.__GetConn()
        try:
            sql = "SELECT " + self.__OPT_FIELD + " FROM " + self.__DB_TABLE + self.__OPT_WHERE + self.__OPT_ORDER + self.__OPT_LIMIT
            result = self.__DB_CONN.execute(sql,self.__OPT_PARAM)
            data = result.fetchall()
            if self.__OPT_FIELD != "*":
                field = self.__OPT_FIELD.split(',')
                tmp = []
                for row in data:
                    i=0
                    tmp1 = {}
                    for key in field:
                        tmp1[key] = row[i]
                        i += 1
                    tmp.append(tmp1)
                    del(tmp1)
                data = tmp
                del(tmp)
            else:
                tmp = map(list,data)
                data = tmp
                del(tmp)
            self.__close()
            return data
        except Exception,ex:
            return "error: " + str(ex)


    def getField(self,keyName):
        result = self.field(keyName).select();
        if len(result) == 1:
            return result[0][keyName]
        return result


    def setField(self,keyName,keyValue):
        return self.save(keyName,(keyValue,))


    def find(self):
        result = self.limit("1").select()
        if len(result) == 1:
            return result[0]
        return result


    def count(self):
        key="COUNT(*)"
        data = self.field(key).select()
        try:
            return int(data[0][key])
        except:
            return 0


    def add(self,keys,param):
        self.__GetConn()
        self.__DB_CONN.text_factory = str
        try:
            values=""
            for key in keys.split(','):
                values += "?,"
            values = values[0:len(values)-1]
            sql = "INSERT INTO "+self.__DB_TABLE+"("+keys+") "+"VALUES("+values+")"
            result = self.__DB_CONN.execute(sql,param)
            id = result.lastrowid
            self.__close()
            self.__DB_CONN.commit()
            return id
        except Exception,ex:
            return "error: " + str(ex)

    def addAll(self,keys,param):
        self.__GetConn()
        self.__DB_CONN.text_factory = str
        try:
            values=""
            for key in keys.split(','):
                values += "?,"
            values = values[0:len(values)-1]
            sql = "INSERT INTO "+self.__DB_TABLE+"("+keys+") "+"VALUES("+values+")"
            result = self.__DB_CONN.execute(sql,param)
            return True
        except Exception,ex:
            return "error: " + str(ex)

    def commit(self):
        self.__close()
        self.__DB_CONN.commit()


    def save(self,keys,param):
        self.__GetConn()
        self.__DB_CONN.text_factory = str
        try:
            opt = ""
            for key in keys.split(','):
                opt += key + "=?,"
            opt = opt[0:len(opt)-1]
            sql = "UPDATE " + self.__DB_TABLE + " SET " + opt+self.__OPT_WHERE

            import public
            public.writeFile('/tmp/test.pl',sql)

            tmp = list(param)
            for arg in self.__OPT_PARAM:
                tmp.append(arg)
            self.__OPT_PARAM = tuple(tmp)
            result = self.__DB_CONN.execute(sql,self.__OPT_PARAM)
            self.__close()
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception,ex:
            return "error: " + str(ex)

    def delete(self,id=None):
        self.__GetConn()
        try:
            if id:
                self.__OPT_WHERE = " WHERE id=?"
                self.__OPT_PARAM = (id,)
            sql = "DELETE FROM " + self.__DB_TABLE + self.__OPT_WHERE
            result = self.__DB_CONN.execute(sql,self.__OPT_PARAM)
            self.__close()
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception,ex:
            return "error: " + str(ex)


    def execute(self,sql,param):
        self.__GetConn()
        try:
            result = self.__DB_CONN.execute(sql,param)
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception,ex:
            return "error: " + str(ex)


    def query(self,sql,param):
        self.__GetConn()
        try:
            result = self.__DB_CONN.execute(sql,param)
            data = map(list,result)
            return data
        except Exception,ex:
            return "error: " + str(ex)

    def create(self,name):
        self.__GetConn()
        import public
        script = public.readFile('data/' + name + '.sql')
        result = self.__DB_CONN.executescript(script)
        self.__DB_CONN.commit()
        return result.rowcount

    def fofile(self,filename):
        self.__GetConn()
        import public
        script = public.readFile(filename)
        result = self.__DB_CONN.executescript(script)
        self.__DB_CONN.commit()
        return result.rowcount

    def __close(self):
        self.__OPT_WHERE = ""
        self.__OPT_FIELD = "*"
        self.__OPT_ORDER = ""
        self.__OPT_LIMIT = ""
        self.__OPT_PARAM = ()

    def close(self):
        try:
            self.__DB_CONN.close()
            self.__DB_CONN = None
        except:
            pass
