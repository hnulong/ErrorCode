# 1.工程功能

该项目主要是用于对EOSXX00000临时错误码进行统一生成错误码。

# 2.环境要求
采用的技术是python3.6+sqlite3

# 3.使用说明
运行master.py文件，将显示一个UI界面，按照按钮说明，设置源目录、目标目录即可，然后点击"执行"按钮执行，生成含有新的错误码文件、新增错误码的sql脚本以及数据库备份数据

# 4.文件说明
```text
a.SC_MSG_CODE.sql：建表脚本
b.clear.sql：数据库清空脚本
c.errorcode.db：数据库文件
d.errorcode.py：生成错误码的类
e.master.py：UI显示界面

```

