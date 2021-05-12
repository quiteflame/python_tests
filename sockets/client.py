import socket
import logging
import errno
import sys

HEADER_SIZE = 10
PACKAGE_SIZE = 10
IP = "192.168.0.33"
PORT = 1337


class Client(object):
    def __init__(self, ip: str, port: int):
        logging.basicConfig(level=logging.INFO)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        self.client_socket.setblocking(False)

    def msg(self, body: str):
        header = f"{len(body):<{HEADER_SIZE}}"
        message = header + body
        logging.info(f"Sending: {message}")
        return bytes(message, "utf-8")

    def receive_message(self):
        header = self.client_socket.recv(HEADER_SIZE)
        total_bytes_to_receive = int(header)
        msg_chunks = []
        remaining_bytes = total_bytes_to_receive
        while True:
            chunk = self.client_socket.recv(min(PACKAGE_SIZE, remaining_bytes))
            msg_chunks.append(str(chunk, "utf-8"))
            remaining_bytes -= min(PACKAGE_SIZE, remaining_bytes)
            if remaining_bytes <= 0:
                return "".join(msg_chunks)

    def run(self):
        self.client_socket.send(self.msg("quiteflame"))
        while True:
            try:
                logging.info(self.receive_message())
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    logging.error(f"Reading error {str(e)}")
                    sys.exit()
                continue


if __name__ == "__main__":
    client = Client(IP, PORT)
    client.run()
