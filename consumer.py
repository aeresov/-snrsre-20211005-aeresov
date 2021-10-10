import json

import kafka
import psycopg2


def dbConn():
    return psycopg2.connect(
        "postgres://avnadmin:be9c1xH2egqw4X2@pg-1af72c59-project-0a6a.aivencloud.com:27821/defaultdb?sslmode=require"
    )


def insert_record(msg):
    conn = dbConn()
    url, status, response_time, match = map(
        msg.get, ['url', 'status', 'response_time', 'match']
    )
    conn.cursor().execute(
        f"""
        insert into webmon_polls (url, status_code, response_time, regex_match)
        values ('{url}', '{status}', '{response_time}', '{match}')
        """
    )
    conn.commit()
    conn.close()


def main():
    import ssl

    ssl_context = ssl.create_default_context(
        purpose=ssl.Purpose.CLIENT_AUTH,
        cafile="ca.pem",
    )
    ssl_context.load_cert_chain(
        certfile="service.cert",
        keyfile="service.key",
    )

    consumer = kafka.KafkaConsumer(
        'webmon',
        bootstrap_servers=["kafka-22ebb710-project-0a6a.aivencloud.com:27823"],
        security_protocol="SSL",
        ssl_context=ssl_context,
        value_deserializer=lambda bs: json.loads(bs.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    for msg in consumer:
        insert_record(msg.value)


if __name__ == "__main__":
    main()
