import requests
import re
import time
import os
import sys
import json
import logging
import kafka
import threading

def poll_site(url, regex=None):
    resp = requests.get(url)
    match = regex and re.search(regex, resp.text)
    return {
        'url': url,
        'status': resp.status_code,
        'response_time': 0,
        'match': match and match.group(0),
    }


def send_message(producer, topic, message):
    # Topic must exist for producer to succeed
    print("sending", message)
    producer.send(topic, json.dumps(message).encode('ascii'))
    producer.flush()


def loop(producer, topic, url, regex=None, interval=15):
    while True:
        send_message(producer, "webmon", poll_site(url, regex))


def main():
    producer = kafka.KafkaProducer(
        bootstrap_servers=["kafka-22ebb710-project-0a6a.aivencloud.com:27823"],
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
        max_block_ms=5000,
    )

    sites = [
        "https://httpstat.us/200",
        "https://httpstat.us/404",
        # "https://httpstat.us/301",
        # "https://httpstat.us/201?sleep=120000",
        "https://tls-v1-2.badssl.com:1012/",
        # "https://expired.badssl.com/",
    ]

    for url in sites:
        threading.Thread(target=loop, args=(producer, "webmon", url)).start()


if __name__ == '__main__':
    main()
