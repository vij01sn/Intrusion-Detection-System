from scapy.all import sniff, IP, TCP
import requests

URL = "http://127.0.0.1:5000/live"

def process(packet):

    if IP in packet:
        proto = "tcp" if TCP in packet else "udp"

        data = {
            "duration": 0,
            "protocol_type": proto,
            "service": "http",
            "flag": "SF",
            "src_bytes": len(packet),
            "dst_bytes": len(packet)
        }

        try:
            requests.post(URL, data=data)
            print("Sent:", data)
        except:
            pass

sniff(prn=process, store=False)