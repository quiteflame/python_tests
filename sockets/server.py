import socket
import logging
import select

HEADER_SIZE = 10
PACKAGE_SIZE = 10
CONNECTION_COUNT = 5
PORT = 1337


class Server(object):
    def __init__(self, port: int):
        logging.basicConfig(level=logging.INFO)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ip = "0.0.0.0"
        self.server_socket.bind((ip, port))
        logging.info(f"Server running on {ip}:{port}")
        self.server_socket.listen(CONNECTION_COUNT)

        self.socket_list = [self.server_socket]
        self.clients = {}

    def msg(self, body: str):
        body += "\r\n"
        header = f"{len(body):<{HEADER_SIZE}}"
        message = header + body
        logging.info(f"Sending: {message}".strip())
        return bytes(message, "utf-8")

    def receive_message(self, s: socket.socket):
        try:
            header = s.recv(HEADER_SIZE)
            total_bytes_to_receive = int(header)
            msg_chunks = []
            remaining_bytes = total_bytes_to_receive
            while True:
                chunk = s.recv(min(PACKAGE_SIZE, remaining_bytes))
                msg_chunks.append(str(chunk, "utf-8"))
                remaining_bytes -= min(PACKAGE_SIZE, remaining_bytes)
                if remaining_bytes <= 0:
                    return "".join(msg_chunks)
        except Exception as e:
            logging.error(e)
            return None

    def run(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    logging.info(f"Connection from {client_address[0]}:{client_address[1]} established")
                    client_socket.send(self.msg("Welcome to the server!"))
                    self.socket_list.append(client_socket)
                    self.clients[client_socket] = client_address
                else:
                    message = self.receive_message(notified_socket)
                    notified_address = self.clients[notified_socket]
                    if message:
                        logging.info(f"Message received from {notified_address[0]}:{notified_address[1]} - {message.strip()}")
                    else:
                        logging.info(f"Connection lost from {notified_address[0]}:{notified_address[1]}")
                        self.socket_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

            for notified_socket in exception_sockets:
                self.socket_list.remove(notified_socket)


if __name__ == "__main__":
    server = Server(PORT)
    server.run()
