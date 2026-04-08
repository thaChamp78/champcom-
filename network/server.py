"""
ChampCom Network Server - REAL TCP/UDP socket networking
This is actual networking, not a stub. Handles connections, message
passing, and peer-to-peer communication over real sockets.
"""
import socket
import threading
import json
import struct
import time
from collections import deque


class Packet:
    """Binary network packet with header + JSON payload."""
    HEADER_FORMAT = "!I"  # 4-byte unsigned int for payload length
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, msg_type, data):
        self.msg_type = msg_type
        self.data = data
        self.timestamp = time.time()

    def encode(self):
        payload = json.dumps({
            "type": self.msg_type,
            "data": self.data,
            "ts": self.timestamp
        }).encode("utf-8")
        header = struct.pack(self.HEADER_FORMAT, len(payload))
        return header + payload

    @staticmethod
    def decode(raw_bytes):
        obj = json.loads(raw_bytes.decode("utf-8"))
        return Packet(obj["type"], obj["data"])


class Connection:
    """Represents a single network peer."""

    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.alive = True
        self.last_seen = time.time()
        self.recv_buffer = b""

    def send_packet(self, packet):
        try:
            self.sock.sendall(packet.encode())
            return True
        except (BrokenPipeError, ConnectionResetError, OSError):
            self.alive = False
            return False

    def recv_packets(self):
        """Non-blocking receive, returns list of decoded packets."""
        packets = []
        try:
            self.sock.setblocking(False)
            data = self.sock.recv(65536)
            if not data:
                self.alive = False
                return packets
            self.recv_buffer += data
            self.last_seen = time.time()
        except BlockingIOError:
            pass
        except (ConnectionResetError, OSError):
            self.alive = False
            return packets

        # Parse complete packets from buffer
        while len(self.recv_buffer) >= Packet.HEADER_SIZE:
            payload_len = struct.unpack(
                Packet.HEADER_FORMAT,
                self.recv_buffer[:Packet.HEADER_SIZE]
            )[0]
            total_len = Packet.HEADER_SIZE + payload_len
            if len(self.recv_buffer) < total_len:
                break
            raw = self.recv_buffer[Packet.HEADER_SIZE:total_len]
            self.recv_buffer = self.recv_buffer[total_len:]
            packets.append(Packet.decode(raw))

        return packets

    def close(self):
        self.alive = False
        try:
            self.sock.close()
        except OSError:
            pass


class TCPServer:
    """Real TCP server for reliable communication."""

    def __init__(self, host="0.0.0.0", port=7777):
        self.host = host
        self.port = port
        self.sock = None
        self.connections = []
        self.running = False
        self.on_packet = None  # callback(connection, packet)
        self.on_connect = None  # callback(connection)
        self.on_disconnect = None  # callback(connection)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.sock.bind((self.host, self.port))
        self.sock.listen(32)
        self.running = True

        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._recv_loop, daemon=True).start()
        print(f"  [NET] TCP server listening on {self.host}:{self.port}")

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.sock.accept()
                conn = Connection(client_sock, addr)
                self.connections.append(conn)
                print(f"  [NET] Client connected: {addr}")
                if self.on_connect:
                    self.on_connect(conn)
            except socket.timeout:
                continue
            except OSError:
                break

    def _recv_loop(self):
        while self.running:
            dead = []
            for conn in self.connections:
                if not conn.alive:
                    dead.append(conn)
                    continue
                packets = conn.recv_packets()
                for pkt in packets:
                    if self.on_packet:
                        self.on_packet(conn, pkt)

            for conn in dead:
                self.connections.remove(conn)
                print(f"  [NET] Client disconnected: {conn.address}")
                if self.on_disconnect:
                    self.on_disconnect(conn)
                conn.close()

            time.sleep(0.016)  # ~60Hz poll

    def broadcast(self, packet):
        for conn in self.connections:
            if conn.alive:
                conn.send_packet(packet)

    def stop(self):
        self.running = False
        for conn in self.connections:
            conn.close()
        if self.sock:
            self.sock.close()
        print("  [NET] TCP server stopped")


class TCPClient:
    """Real TCP client for connecting to a ChampCom server."""

    def __init__(self):
        self.conn = None
        self.running = False
        self.on_packet = None
        self.send_queue = deque()

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self.conn = Connection(sock, (host, port))
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        print(f"  [NET] Connected to {host}:{port}")

    def _loop(self):
        while self.running and self.conn and self.conn.alive:
            # Send queued packets
            while self.send_queue:
                pkt = self.send_queue.popleft()
                self.conn.send_packet(pkt)

            # Receive
            packets = self.conn.recv_packets()
            for pkt in packets:
                if self.on_packet:
                    self.on_packet(pkt)

            time.sleep(0.016)

    def send(self, packet):
        self.send_queue.append(packet)

    def disconnect(self):
        self.running = False
        if self.conn:
            self.conn.close()


class UDPSocket:
    """Real UDP socket for fast unreliable data (game state, voice, etc)."""

    def __init__(self, host="0.0.0.0", port=7778):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.on_receive = None  # callback(data, address)
        self.peers = set()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5)
        self.sock.bind((self.host, self.port))
        self.running = True
        threading.Thread(target=self._recv_loop, daemon=True).start()
        print(f"  [NET] UDP socket bound on {self.host}:{self.port}")

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65536)
                self.peers.add(addr)
                if self.on_receive:
                    self.on_receive(data, addr)
            except socket.timeout:
                continue
            except OSError:
                break

    def send_to(self, data, address):
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            self.sock.sendto(data, address)
        except OSError:
            pass

    def broadcast(self, data):
        for peer in self.peers:
            self.send_to(data, peer)

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
