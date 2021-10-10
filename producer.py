import logging
import re
from typing import Optional

import kafka
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

import boilerplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
scheduler = BlockingScheduler()


def poll_site(
    url: str,
    regex: Optional[str] = None,
) -> Optional[boilerplate.Message]:
    try:
        logger.info(f"requesting {url}")
        resp = requests.get(url)
        match = regex and re.search(regex, resp.text)
        return boilerplate.Message(
            url=url,
            status=resp.status_code,
            response_time=resp.elapsed,
            match=match and match.group(0),
        )
    except requests.exceptions.RequestException as rex:
        logger.error(rex.error.msg)
        return None


def loop(
    producer: kafka.KafkaProducer,
    topic: str,
    url: str,
    regex: Optional[str] = None,
):
    payload = poll_site(url, regex)
    if payload:
        logger.info(f"sending: {payload}")
        producer.send(topic, payload.json().encode("utf-8"))


def main():
    producer = kafka.KafkaProducer(
        bootstrap_servers=[boilerplate.KAFKA_HOST],
        security_protocol="SSL",
        ssl_context=boilerplate.create_ssl_context(),
        max_block_ms=5000,
        linger_ms=0,
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
        scheduler.add_job(
            loop,
            kwargs={
                "producer": producer,
                "topic": boilerplate.KAFKA_TOPIC,
                "url": url,
            },
            trigger=IntervalTrigger(seconds=15),
        )
    scheduler.start()


if __name__ == '__main__':
    main()
