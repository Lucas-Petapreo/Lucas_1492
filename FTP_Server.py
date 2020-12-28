"""
    FTP服务器
    多线程并发网络
"""
from socket import *
import sys
from threading import Thread
import os
from time import sleep

# 全局变量
HOST = '0.0.0.0'
PORT = 12345
ADDR = (HOST, PORT)
FTP = './FTP/'  # 文件库存放位置


# 文件传输功能
class FtpServer:
    def __init__(self, conn, ftp_path):
        self.conn = conn
        self.ftp_path = ftp_path

    def do_list(self):
        # listdir能找到隐藏文件，所以要过滤
        lst_files = os.listdir(self.ftp_path)
        if not lst_files:
            self.conn.send(b'File Dir is Empty.')
            return
        else:
            # 如此 四次发送，必定会沾包，接收错乱
            # 方案1： sleep(0.1) 每个send后加
            # 方案2： 认为添加边界，比如“\n"
            self.conn.send(b'OK')
            # sleep防止和后面沾包
            sleep(0.1)
            # --------以下为循环发送-------------#
            # --------沾包严重------------------#
        # for file in lst_files:
        # ‘.'保证不是隐藏，os.path.isfile保证是普通文件
        # if file[0] != '.' and \
        #         os.path.isfile(self.ftp_path + file):
        #     self.conn.send(file.encode())
        # sleep(0.1)
        # ------------以下为人为添加边界-----------#
        str_files = ''
        for file in lst_files:
            if file[0] != '.' and \
                    os.path.isfile(self.ftp_path + file):
                str_files += file + '\n'
        # str_files += '##'
        self.conn.send(str_files.encode())
        # sleep(0.1)

    def do_get(self, filename):
        try:
            obj_file = open(self.ftp_path + filename, 'rb')
        except Exception:
            self.conn.send('File Not Found Error.'.encode())
            return
        else:
            self.conn.send(b'OK')
            sleep(0.1)
        # 发送文件
        while True:
            data = obj_file.read(1024)
            if not data:
                sleep(0.1)
                self.conn.send(b'##')
                break
            self.conn.send(data)
        obj_file.close()

    def do_put(self, filename):
        if os.path.exists(self.ftp_path + filename):
            self.conn.send(b'File Already Exist.')
            return
        else:
            self.conn.send(b'OK')
            # 因为下面是接收，所以不用sleep
            # sleep(0.1)
        # 接收文件
        obj_file = open(self.ftp_path + filename, 'wb')
        while True:
            data = self.conn.recv(1024)
            if data == b'##':
                break
            obj_file.write(data)
        obj_file.close()


# 客户端请求函数
def handle(conn):
    cls_file = conn.recv(1024).decode()
    ftp_path = FTP + cls_file + '/'
    # 因为后续上传下载都需要在ftp_path下操作
    ftp = FtpServer(conn, ftp_path)
    while True:
        data = conn.recv(1024).decode()
        # 后面可能会有其他请求需要'L'+***，为了
        # 保持风格的统一，使用data[0]
        # 如果客户端断开返回值为空
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)

        # 网络构建


def main():
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    sockfd.bind(ADDR)
    print('Wait For Connection...')
    sockfd.listen()
    # 监听客户端的请求
    while True:
        try:
            conn, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit('Server Exit !')
        except Exception as e:
            print(e)
            continue
        # 建立线程处理客户端请求
        print("Connect from ", addr)
        cur_thread = Thread(target=handle, args=(conn,))
        cur_thread.setDaemon(True)
        cur_thread.start()


if __name__ == '__main__':
    main()
