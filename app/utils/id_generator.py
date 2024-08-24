import time
import ulid


def order_id() -> str:
    return str(ulid.from_timestamp(time.time()))
