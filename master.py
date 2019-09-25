# -*- coding:utf-8 -*-
# __author__ = 'Code~'

import os
import traceback
import tkinter
from tkinter import *
from tkinter import filedialog, ttk
from tkinter import messagebox
# from . import  errorcode
from errorcode import ErrorCodeManager

DEF_PATH = r''


# 消息框模块
class MsgBox:
    def __init__(self):
        #
        self.codemanager = ErrorCodeManager()
        # 目录相关
        self.root = tkinter.Tk()
        self.root.title("错误码生成工具")
        self.root.geometry("800x600")
        self.showMsgBox()
        self.root.mainloop()

    # 显示消息框
    def showMsgBox(self):
        """

        :return:
        """
        root = self.root

        fm1 = Frame(root)
        #
        Label(fm1, text='  源目录:').grid(row=1, column=0, sticky='E')
        self.csdVar = StringVar()
        self.csdVar.set(DEF_PATH)
        Entry(fm1, textvariable=self.csdVar, width=50).grid(row=1, column=1)
        # Button(fm1, text='打开文件', command=self.openFileEvent).grid(row=1, column=2)
        Button(fm1, text='打开目录', command=self.openDirEvent).grid(row=1, column=2)
        fm1.pack(fill=BOTH, expand=NO)
        #
        fm2 = Frame(root)
        Label(fm2, text='输出目录:').grid(row=1, column=0, sticky='E')
        self.outVar = StringVar()
        self.outVar.set(DEF_PATH)
        Entry(fm2, textvariable=self.outVar, width=50).grid(row=1, column=1)
        Button(fm2, text='另存为', command=self.selectOutPathEvent).grid(row=1, column=2)
        Button(fm2, text='执行', command=self.execute).grid(row=1, column=3, padx=10)
        fm2.pack(fill=BOTH, expand=NO, pady=20)
        #
        #
        self.listview = Listbox()
        # listview.grid(row=3,columnspan=3, sticky='W')
        self.listview.pack(side=TOP, anchor=N, fill=BOTH, expand=YES)
        # for i in range(20):
        #     self.listview.insert(0,"wwwww"+str(i))
        #
        #     #
        fm3 = Frame(root)
        Label(fm3, text='数据库导入文件:').grid(row=1, column=0, sticky='E')
        self.dbFilenameEnt = StringVar()
        self.dbFilenameEnt.set(DEF_PATH)
        Entry(fm3, textvariable=self.dbFilenameEnt, width=50).grid(row=1, column=1)
        Button(fm3, text='导入', command=self.openDbFile).grid(row=1, column=2)
        Button(fm3, text='导出', command=self.saveDbFile).grid(row=1, column=3, padx=10)
        fm3.pack(fill=BOTH, expand=NO, pady=3)

    # 打开文件
    def openFileEvent(self):
        """

        :return:
        """
        newDir = filedialog.askopenfilename(initialdir=DEF_PATH, title='打开新文件')
        if len(newDir) == 0:
            return
        self.csdVar.set(newDir)

    # 打开目录
    def openDirEvent(self):
        """

        :return:
        """
        newDir = filedialog.askdirectory(initialdir=DEF_PATH, title='打开目录')
        if len(newDir) == 0:
            return
        self.csdVar.set(newDir)
        self.codemanager.srcPath = newDir
        self.codemanager.logger.info("src:%s" % self.codemanager.srcPath)
        # self.listview.insert(0,newDir)

    # 另存为
    def selectOutPathEvent(self):
        """

        :return:
        """
        newDir = filedialog.askdirectory(initialdir=DEF_PATH, title='打开目录')
        if len(newDir) == 0:
            return
        self.outVar.set(newDir)
        self.codemanager.newScrPath = newDir
        self.codemanager.logger.info("dest:%s" % self.codemanager.newScrPath)

    def execute(self):
        """

        :return:
        """
        self.listview.insert(0, "开始对***00000错误码进行编码")
        try:
            mpb = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
            mpb.pack()
            mpb["maximum"] = 100
            mpb["value"] = 0
            up_label = Label(self.root, text='正在执行...', fg='red')
            up_label.pack()

            filenames = self.codemanager.execute()
            # 若为空目录，则直接返回
            if len(filenames) == 0:
                self.codemanager.logger.info('empty directory!')
                return

            index = 0
            for filename in filenames:
                self.codemanager.generate_new_error_code_file(filename)
                mpb["value"] = (index * 100) // len(filenames) + 1
                self.root.update()
                index += 1

            self.codemanager.export_info()

            self.listview.insert(0, "执行完毕！")
            tkinter.messagebox.showinfo('提示', "执行完毕！")
        except:
            tkinter.messagebox.showerror('错误', '出错了')
        finally:
            # 销毁进度条
            mpb.pack_forget()
            up_label.pack_forget()
            return

    def openDbFile(self):
        """
        导入数据库信息
        :return:
        """
        filename = filedialog.askopenfilename(initialdir=DEF_PATH, title='打开新文件')
        if len(filename) == 0:
            return
        self.dbFilenameEnt.set(filename)
        self.listview.insert(0, "打开的数据库文件名为：%s" % filename)

        # 读取文件数据
        self.listview.insert(0, " 开始导入数据...")
        # self.codemanager.clear_db()
        # self.listview.insert(0, filename.split('.')[1])
        # if filename.split('.')[1] == 'sql':
        srcFile = open(filename, mode='r', encoding='utf-8')
        data = srcFile.readlines()
        sqlset = []
        for line in data:
            # template = re.compile(r"(\w+)'(\w+)")
            # while line != re.sub(template, r"\1''\2", line):
            #     line = re.sub(template, r"\1''\2", line)
            # template = re.compile(r"'([^'\s\S]+)'(\w+.*\w+)'([^'\s\S]+)'\);")
            # while line != re.sub(template, r"'\1''\2''\3'\);", line):
            #     line = re.sub(template, r"'\1''\2''\3'\);", line)
            # self.codemanager.logger.info(line)
            sqlset.append(line)
            # self.listview.insert(0,line)
        srcFile.close()
        self.codemanager.execute_db(sqlset)
        self.listview.insert(0, " 导入数据成功！")
        tkinter.messagebox.showinfo('提示', " 导入数据成功！")

    def saveDbFile(self):
        """

        :return:
        """
        filename = filedialog.askopenfilename(initialdir=DEF_PATH, title='打开新文件')
        if len(filename) == 0:
            filename = os.path.join(os.path.curdir, 'bcp.txt')
        self.dbFilenameEnt.set(filename)
        self.listview.insert(0, "导出文件路径为%s" % filename)

        self.codemanager.bcp_db(filename)
        tkinter.messagebox.showinfo('提示', " 导出数据成功！")


if __name__ == "__main__":
    try:
        messageBox = MsgBox()
    except Exception:
        traceback.print_exc()
