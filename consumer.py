import logging
from contextlib import closing

import kafka
import psycopg2
from psycopg2 import sql

import boilerplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dbConn():
    return psycopg2.connect(boilerplate.PG_DSN)


def insert_record(msg: boilerplate.Message):
    query = sql.SQL(
        "INSERT INTO webmon_polls (url, status_code, response_time, regex_match) "  # noqa
        "VALUES (%s, %s, %s, %s);"
    )
    try:
        with closing(dbConn()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        str(msg.url),
                        msg.status,
                        msg.response_time,
                        msg.match,
                    ),
                )
                conn.commit()
    except psycopg2.Error as pge:
        logger.error(pge.pgerror)


def main():
    consumer = kafka.KafkaConsumer(
        boilerplate.KAFKA_TOPIC,
        bootstrap_servers=[boilerplate.KAFKA_HOST],
        security_protocol="SSL",
        ssl_context=boilerplate.create_ssl_context(),
        value_deserializer=lambda bs: boilerplate.Message.parse_raw(
            bs, encoding="utf-8"
        ),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    for msg in consumer:
        insert_record(msg.value)


if __name__ == "__main__":
    main()
