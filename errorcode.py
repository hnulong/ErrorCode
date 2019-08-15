# coding:utf-8

import os
import re
import csv
import sqlite3
import logging
import logging.config
from logging import handlers

"""
错误码的生成与管理
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True  # 标记是否在开发环境


# 给过滤器使用的判断
class RequireDebugTrue(logging.Filter):
    """

    """

    # 实现filter方法
    def filter(self, record):
        return DEBUG


class ErrorCodeManager(object):
    def __init__(self):
        """

        """
        # 设置日志处理
        log_config = {
            "version": 1,
            'disable_existing_loggers': False,  # 是否禁用现有的记录器

            # 日志管理器集合
            'loggers': {
                # 管理器
                'default': {
                    'handlers': ['console', 'log'],
                    'level': 'DEBUG',
                    'propagate': True,  # 是否传递给父记录器
                },
            },

            # 处理器集合
            'handlers': {
                # 输出到控制台
                'console': {
                    'level': 'DEBUG',  # 输出信息的最低级别
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',  # 使用standard格式
                    'filters': ['require_debug_true', ],  # 仅当 DEBUG = True 该处理器才生效
                },
                # 输出到文件
                'log': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'standard',
                    'filename': './log/all.log',  # 输出位置
                    'maxBytes': 1024 * 1024 * 5,  # 文件大小 5M
                    'backupCount': 5,  # 备份份数
                    'encoding': 'utf8',  # 文件编码
                },
            },
            # 过滤器
            'filters': {
                'require_debug_true': {
                    '()': RequireDebugTrue,
                }
            },

            # 日志格式集合
            'formatters': {
                # 标准输出格式
                'standard': {
                    # [具体时间][线程名:线程ID][日志名字:日志级别名称(日志级别ID)] [输出的模块:输出的函数]:日志内容
                    'format': '[%(asctime)s][%(name)s:%(levelname)s(%(lineno)d)]--[%(module)s]:%(message)s'
                }
            }
        }

        logging.config.dictConfig(log_config)
        self.logger = logging.getLogger("default")

        # self.logger = logging.getLogger(__name__)
        # log_file = "./log/all.log"
        # # fh = handlers.RotatingFileHandler(filename=log_file,maxBytes=10,backupCount=3)
        # fh = handlers.TimedRotatingFileHandler(filename=log_file, when="D", interval=1,
        #                                        backupCount=3)  # filename定义将信息输入到指定的文件，
        # # when指定单位是s(秒),interval是时间间隔的频率,单位是when所指定的哟（所以，你可以理解频率是5s）；backupCount表示备份的文件个数，我这里是指定的3个文件。
        # formatter = logging.Formatter('%(asctime)s %(module)s:%(lineno)d %(message)s')  # 定义输出格式
        # fh.setFormatter(formatter)  # 添加格式化输出
        # fh.suffix = "%Y-%m-%d_%H-%M-%S.log"
        # self.logger.addHandler(fh)
        # self.logger.setLevel(logging.INFO)

        self.srcPath = r'./old'
        self.newScrPath = r'./new'
        self.errCodeFile = r'errorcode.db'
        # self.centreid = '999999'
        # self.bankno = '999999'
        self.fixlen = 5

        self.error_flag = '('
        # warn_flag = 'warn('
        self.module_list = ['LM', 'CM', 'GL', 'MT', 'SE']

        self.errmap = {}
        self.new_error_code_dict = {}
        # 设置一个集合用于存最新的错误码
        self.errorcodeset=set()

    def search_all_files(self, base):
        """
        查找目录下的所有文件
        """
        filelist = os.listdir(base)
        res = []
        for filename in filelist:
            fullname = os.path.join(base, filename)
            self.logger.debug(fullname)
            if os.path.isfile(fullname):
                res.append(fullname)
            else:
                res.extend(self.search_all_files(fullname))
        return res

    def to_excel(self, data, filename):
        """

        :param data:
        :param filename:
        :return:
        """
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(data)

    def from_excel(self, filename):
        """

        :param filename:
        :return:
        """
        data = []
        with open(filename) as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
        return data

    def to_code(self, n):
        """

        :param n:
        :return:
        """
        self.logger.debug(n)
        codeset = '0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
        l = len(codeset)
        res = ''
        while n > 0:
            r = n % l
            res = codeset[r] + res
            n = n // l
        return res

    def to_num(self, code):
        """

        :param code:
        :return:
        """
        codeset = r'0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
        l = len(codeset)
        n = 0
        for c in code:
            n *= l
            if c not in codeset:
                return 0
            n += codeset.index(c)
        return n

    def load_error_code_file(self):
        """
        加载错误码信息
        errCodeFileName 错误码文件
        fixLen 每个模块的固定位数
        """
        self.errmap.clear()
        conn = sqlite3.connect(self.errCodeFile)
        cur = conn.cursor()
        sql = '''select * from SC_MSG_CODE'''
        cur.execute(sql)
        for row in cur:
            self.logger.debug(row)
            errcode = row[2]
            # 记录当前编码的最新位置
            if errcode[:self.fixlen] not in self.errmap:
                self.errmap[errcode[:self.fixlen]] = 0
            n = self.to_num(errcode[self.fixlen:])
            if self.errmap[errcode[:self.fixlen]] < n:
                self.errmap[errcode[:self.fixlen]] = n
        cur.close()
        conn.close()

    def is_table_empty(self):
        """
        判断错误码的表是否为空
        """

        flag = False
        conn = sqlite3.connect(self.errcodefilename)
        cur = conn.cursor()
        sql = '''select distinct code from SC_MSG_CODE'''
        cur.execute(sql)
        if len(list(cur)) > 0:
            flag = True
        cur.close()
        conn.close()
        return flag

    def generate_new_error_code_file(self, filename):
        """
        产生新的错误码，同时替换掉00000结尾的临时错误码，生成新的文件
        """
        srcFileName = filename
        newFileName = filename.replace(self.srcPath, self.newScrPath)
        # logger.info(newFileName)
        newFilePath = os.path.split(newFileName)[0]
        if not os.path.exists(newFilePath):
            os.makedirs(newFilePath)
        srcFile = open(srcFileName, mode='r', encoding='utf-8')
        data = srcFile.readlines()
        srcFile.close()

        n = 0
        newData = []
        while n < len(data):
            # funcflag为error or warn
            if data[n].strip().startswith('error(') or data[n].strip().startswith('warn('):
                self.logger.debug(data[n])
                # 说明error or warn信息没有被分行
                newMsg = data[n]
                info = ''
                if data[n].strip().endswith(');'):
                    newMsg = self.get_error_code_message(data[n], filename)
                else:
                    while not data[n].strip().endswith(');'):
                        info += data[n].replace('\n', '').strip()
                        n += 1
                    info += data[n].replace('\n', '').strip()
                    # print('******',info)
                    newMsg = self.get_error_code_message(info, filename)
                if not newMsg:
                    n += 1
                    continue

                newData.append(newMsg.rstrip())
            else:
                newData.append(data[n].rstrip())
            n += 1

        newFile = open(newFileName, 'w', encoding='utf-8')
        for line in newData:
            newFile.write(line + '\n')
        newFile.close()

    def generat_new_error_code(self, msg):
        """
        按照规则生成新的错误码5+5

        :param msg:
        :param errMap:
        :return:
        """
        self.logger.debug(msg)
        profix = msg[:self.fixlen]
        self.logger.debug([profix,self.fixlen])
        if profix not in self.errmap:
            self.errmap[profix] = 0
        self.errmap[profix] += 1
        self.logger.debug(self.errmap[profix])
        newErrorCode = profix + self.to_code(self.errmap[profix]).rjust(self.fixlen, '0')
        self.logger.debug(newErrorCode)
        return newErrorCode

    def get_error_code_message(self, msg, filename):
        """
        获取错误码信息
        :param msg:
        :return:
        """

        modulename = os.path.splitext(os.path.split(filename)[1])[0][0:2]
        self.logger.debug(filename)
        self.logger.debug(msg)
        searchObj = re.search(r'[ew]\w+?\("([\w]*?)"\);$', msg, re.M | re.I)
        if searchObj:
            return msg
        split_flag = '('
        new_msg = msg[0:msg.find(split_flag) + len(split_flag)]
        errorcode = ''
        try:
            p1 = re.compile(r'[\(](.*)[\)];')  # 最长匹配
            data = re.findall(p1, msg.replace('\n', ''))[0]  # 匹配花括号里面的数据
            self.logger.debug(data)
            p2 = re.compile(r'"(.*?)"[, ]+"(.*?)"(.*)')
            res = re.findall(p2, data)[0]
            # res = list(filter(lambda s: s and (type(s) != str or len(s.strip()) > 0), res))
            # 判断该错误码是否是临时错误码，如果不是则对其进行重编编码
            errorcode = str(res[0]).upper()
        except:
            self.logger.info(filename)
            self.logger.info(msg)
            # raise ValueError('参数错误')
            return

        # 校验错误码前5位　是否正确
        if modulename in self.module_list and modulename != errorcode[3:5]:
            self.logger.error(filename)
            self.logger.error(errorcode)
            return

        if errorcode.endswith("00000"):
            newErrorCode = self.generat_new_error_code(errorcode)
            self.logger.debug(newErrorCode)
            self.new_error_code_dict[newErrorCode] = res[1]
            # 将增量错误码加入集合
            self.errorcodeset.add(newErrorCode)
            tmp = new_msg
            new_msg = tmp[0:len(tmp)-6]+r'// "'+res[1]+'"\n'+tmp
            if len(res) > 2:
                new_msg += '"' + newErrorCode + '"' + res[2] + ');'
            else:
                new_msg += '"' + newErrorCode + '");'
        else:
            # 将存量错误码加入集合
            self.errorcodeset.add(errorcode)
        self.logger.debug(new_msg)

        return new_msg

    def clear_db(self):
        """
        清空数据库表
        :param errcodefilename:
        :return:
        """
        conn = sqlite3.connect(self.errCodeFile)
        c = conn.cursor()
        sql = "delete from SC_MSG_CODE"
        c.execute(sql)
        conn.commit()
        conn.close()

    def execute_db(self, sqlset):
        """

        :param sqlset:
        :return:
        """
        conn = sqlite3.connect(self.errCodeFile)
        c = conn.cursor()
        try:
            for sql in sqlset:
                self.logger.debug(sql)
                c.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def operate_db(self):
        """
        插入数据库操作
        :param errcodefilename:
        :param sqlset:
        :return:
        """

        conn = sqlite3.connect(self.errCodeFile)
        c = conn.cursor()
        try:
            for k, v in self.new_error_code_dict.items():
                sql = "delete from SC_MSG_CODE where code=?"
                c.execute(sql, [k])
                sql = "insert into SC_MSG_CODE (centre_id, bank_no, code, lang, name) values ('999999','999999',?, 'en_US', ?);"
                self.logger.debug(sql)
                c.execute(sql, [k, v])
            conn.commit()
        finally:
            conn.close()

    def bcp_db(self, bcpfilename):
        """
        加载错误码信息
        errCodeFileName 错误码文件
        fixLen 每个模块的固定位数
        """

        conn = sqlite3.connect(self.errCodeFile)
        cur = conn.cursor()
        sql = '''select * from SC_MSG_CODE'''
        cur.execute(sql)
        f = open(bcpfilename, 'w', encoding='utf-8')
        collumnflag = '|!'
        rowflag = '!@!'
        for row in cur:
            # 判断当前错误码是否还在使用，若未使用，则从数据库清除
            if row[2] not in self.errorcodeset:
                sql = "delete from SC_MSG_CODE where code='" + row[2] + "';"
                cur.execute(sql)
                self.logger.debug(sql)
            res = ''
            for tmp in row:
                res += collumnflag + tmp
            f.write(rowflag + res + '\n')

        cur.close()
        conn.close()
        f.close()

    def execute(self):
        self.logger.info("开始对***00000错误码进行编码")
        self.logger.info("读取存量错误码信息")
        # if self.isTableEmpty(self.errCodeFile):
        #     self.codemanager.logger.info("对所有错误码进行编码")
        self.load_error_code_file()

        self.logger.info("扫描文件信息")
        filenames = self.search_all_files(self.srcPath)
        filenames = [filename for filename in filenames if filename.lower().endswith('.java')]
        # 若为空目录，则直接返回
        if len(filenames):
            return

        for filename in filenames:
            self.generate_new_error_code_file(filename)

        # 将新生成的错误码信息写入文件作为变更的脚本
        self.logger.info('将新生成的错误码信息写入文件作为变更的脚本...')
        f = open(os.path.join(self.newScrPath, 'SC_MSG_CODE.txt'), 'w', encoding='utf-8')
        for k, v in self.new_error_code_dict.items():
            # logger.info([k,v])
            v = str(v).replace("'", "''")
            sql = "delete from SC_MSG_CODE where code='" + k + "';\n"
            f.write(sql)
            self.logger.debug(sql)
            sql = "insert into SC_MSG_CODE (centre_id, bank_no, code, lang, name) values ('%s','%s','%s', 'en_US', '%s');\n" % (
                '999999', '999999', k, v)
            f.write(sql)
            self.logger.debug(sql)

        f.close()

        # 写入数据库
        self.logger.info("导出数据库文件...")
        self.operate_db()
        self.bcp_db(os.path.join(self.newScrPath, 'bcp.txt'))


if __name__ == '__main__':
    ecm = ErrorCodeManager()
    ecm.search_all_files(ecm.srcPath)
