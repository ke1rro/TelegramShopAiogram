import io
import csv
from datetime import datetime, timezone

from aiogram.types import BufferedInputFile

from app.database.models import User


async def convert_users_to_csv(users: list[User]) -> BufferedInputFile:
    columns = User.__table__.columns
    data = [[getattr(user, column.name) for column in columns] for user in users]

    s = io.StringIO()
    writer = csv.writer(s, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    writer.writerows(data)
    s.seek(0)

    return BufferedInputFile(
        file=s.getvalue().encode("utf-8-sig"),
        filename=f"users_{datetime.now(timezone.utc).strftime('%Y.%m.%d_%H.%M')}.csv",
    )
