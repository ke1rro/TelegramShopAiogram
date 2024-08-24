import io
import csv

from datetime import datetime, timezone

from aiogram.types import BufferedInputFile

from app.database.models import OrderByCard


async def convert_orders_to_csv(orders: list[OrderByCard]) -> BufferedInputFile:
    columns = OrderByCard.__table__.columns
    data = [[getattr(order, column.name) for column in columns] for order in orders]

    s = io.StringIO()
    writer = csv.writer(s, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    writer.writerows(data)
    s.seek(0)

    return BufferedInputFile(
        file=s.getvalue().encode("utf-8-sig"),
        filename=f"orders_{datetime.now(timezone.utc).strftime('%Y.%m.%d_%H.%M')}.csv",
    )
