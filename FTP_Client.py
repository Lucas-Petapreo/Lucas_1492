"""
    FTP服务端
    多线程并发网络
"""
from socket import *
import sys
from time import sleep

# 全局变量
HOST = '127.0.0.1'
PORT = 12345
ADDR = (HOST, PORT)


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # 请求成功
        if data == 'OK':
            # 尝试循环接收
            # 以下为循环接收客户端
            # while True:
            #     data = self.sockfd.recv(128).decode()
            #     if data == '##':
            #         break
            #     print(data)
            # -------------方案二————认为添加边界-----
            # 接收文件列表
            data = self.sockfd.recv(4028).decode()
            print(data)
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('Thanks For Using.')

    def do_get(self, filename):
        # 发送请求
        self.sockfd.send(('G ' + filename).encode())
        # 等待响应
        data = self.sockfd.recv(128)
        if data == b'OK':
            obj_file = open(filename, 'wb')
            # 接收内容写入文件
            while True:
                cur_data = self.sockfd.recv(1024)
                if cur_data == b'##':
                    break
                obj_file.write(cur_data)
            # 需要关闭文件编辑
            obj_file.close()
        else:
            print(data.decode())

    def do_put(self, filename):
        # 查看文件是否存在
        try:
            obj_file = open(filename, 'rb')
        except Exception:
            print('File Not Exist.')
            return
        else:
            self.sockfd.send(('P '+filename).encode())
            sleep(0.1)
        # 接收服务器回应
        re_sig = self.sockfd.recv(128)
        if re_sig == b'OK':
            # 发送文件
            while True:
                data = obj_file.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
        else:
            print(re_sig.decode())
        obj_file.close()

# 发起请求
def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print('\n\t=========== Order Choice ===========')
        print('\t************** List **************')
        print('\t************ Get File ************')
        print('\t************ Put File ************')
        print('\t************** Quit **************')
        print('\t==================================')

        cmd = input("Input Your Order >>")
        if cmd == 'List':
            ftp.do_list()
        elif cmd[:3] == 'Get':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'Put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)
        elif cmd == 'Quit':
            ftp.do_quit()


def main():
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("Server Connect Fail ...")
        return
    else:
        print('*' * 30, '\n\tData\tFile\tImage\n', '*' * 30)
        cls_file = input("Input File Class >>")
        if cls_file not in ('Data', 'File', 'Image'):
            print("Input Error.")
            return
        else:
            sockfd.send(cls_file.encode())
            request(sockfd)


if __name__ == '__main__':
    main()
