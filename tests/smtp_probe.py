"""Send a single message to hello@verisitu.com via the local SMTP listener.

Usage (on the mail host):
    python3 smtp_probe.py [subject]

Prints the SMTP transcript so the caller can assert that the recipient was
accepted and the message queued for delivery.
"""
import socket
import sys
import time

HOST = "127.0.0.1"
PORT = 25
SUBJECT = sys.argv[1] if len(sys.argv) > 1 else "verisitu routing probe"


def read_reply(stream):
    data = b""
    while True:
        chunk = stream.readline()
        if not chunk:
            break
        data += chunk
        # A complete reply ends with "<code><space>" on its final line.
        if len(chunk) >= 4 and chunk[3:4] == b" ":
            break
    return data.decode(errors="replace").strip()


def main():
    body = (
        "From: probe@verisitu.com\r\n"
        "To: hello@verisitu.com\r\n"
        f"Subject: {SUBJECT}\r\n"
        "Message-Id: <verisitu-probe@example.org>\r\n"
        "Date: Mon, 10 Nov 2026 12:00:00 +0000\r\n"
        "\r\n"
        "routing probe body\r\n"
    )

    sock = socket.create_connection((HOST, PORT), timeout=20)
    stream = sock.makefile("rwb")

    def send(line):
        print("C:", line)
        stream.write((line + "\r\n").encode())
        stream.flush()
        reply = read_reply(stream)
        if reply:
            print("S:", reply)
        return reply

    print("S:", read_reply(stream))
    send("EHLO probe")
    send("MAIL FROM:<probe@verisitu.com>")
    send("RCPT TO:<hello@verisitu.com>")
    send("DATA")
    # Write body and terminator together so smtpd sees a complete message.
    stream.write(body.encode() + b".\r\n")
    stream.flush()
    print("S:", read_reply(stream))
    send("QUIT")
    sock.close()


if __name__ == "__main__":
    main()
