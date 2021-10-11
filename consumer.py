import logging
from contextlib import closing

import kafka
import psycopg2
from psycopg2 import sql
from pydantic.error_wrappers import ValidationError

import boilerplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dbConn():
    return psycopg2.connect(boilerplate.app_settings.pg_dsn)


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
        logger.error(f"db insert unsuccessful: {str(pge)}")


def main():
    try:
        consumer = kafka.KafkaConsumer(
            boilerplate.app_settings.kafka_topic,
            bootstrap_servers=[boilerplate.app_settings.kafka_host],
            security_protocol="SSL",
            ssl_context=boilerplate.create_ssl_context(),
            auto_offset_reset="earliest",
            group_id="dummy",
            enable_auto_commit=True,
        )

        for msg in consumer:
            try:
                message = boilerplate.Message.parse_raw(
                    msg.value,
                    encoding="utf-8",
                )
                insert_record(message)
            except ValidationError as ve:
                logger.error(f"parsing message unsuccessful: {str(ve)}")

    except Exception:
        logger.exception("unexpected error, exiting")


if __name__ == "__main__":
    main()
