import logging
import re
from typing import Optional

import kafka
import requests
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from kafka.errors import KafkaTimeoutError

import boilerplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
scheduler = BlockingScheduler()


def http_request(
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
        logger.error(f"http request unsuccessful: {str(rex)}")
        return None


def poll(
    producer: kafka.KafkaProducer,
    topic: str,
    url: str,
    regex: Optional[str] = None,
):
    payload = http_request(url, regex)
    if payload:
        logger.info(f"sending: {payload}")
        try:
            producer.send(topic, payload.json().encode("utf-8"))
        except KafkaTimeoutError as kte:
            logger.error(f"sending message unsuccessful: {str(kte)}")


def main():
    try:
        producer = kafka.KafkaProducer(
            bootstrap_servers=[boilerplate.app_settings.kafka_host],
            security_protocol="SSL",
            ssl_context=boilerplate.create_ssl_context(),
            max_block_ms=5000,
            linger_ms=0,
        )

        sites = [
            "https://httpstat.us/200",
            "https://httpstat.us/404",
            "https://httpstat.us/301",
            "https://httpstat.us/201?sleep=120000",
            "https://tls-v1-2.badssl.com:1012/",
            "https://expired.badssl.com/",
        ]

        for url in sites:
            scheduler.add_job(
                poll,
                kwargs={
                    "producer": producer,
                    "topic": boilerplate.app_settings.kafka_topic,
                    "url": url,
                },
                name=url,
                trigger=IntervalTrigger(seconds=15),
            )
        scheduler.add_listener(
            lambda e: scheduler.remove_job(e.job_id),
            EVENT_JOB_ERROR,
        )
        scheduler.start()

    except Exception:
        logger.exception("unexpected error, exiting")


if __name__ == '__main__':
    main()
