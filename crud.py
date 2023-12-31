from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import CreateTempData, Temp
from loguru import logger
from fastapi import Request
from lnurl import encode as lnurl_encode

async def create_temp(wallet_id: str, data: CreateTempData) -> Temp:
    temp_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO tempextension.temp (id, wallet, name, lnurlpayamount, lnurlwithdrawamount)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            temp_id,
            wallet_id,
            data.name,
            data.lnurlpayamount,
            data.lnurlwithdrawamount
        ),
    )
    temp = await get_temp(temp_id)
    assert temp, "Newly created temp couldn't be retrieved"
    return temp


async def get_temp(temp_id: str) -> Optional[Temp]:
    row = await db.fetchone("SELECT * FROM tempextension.temp WHERE id = ?", (temp_id,))
    return Temp(**row) if row else None

async def get_temps(wallet_ids: Union[str, List[str]], req: Request) -> List[Temp]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM tempextension.temp WHERE wallet IN ({q})", (*wallet_ids,)
    )
    tempRows = [Temp(**row) for row in rows]
    logger.debug(req.url_for("temp.api_lnurl_pay", temp_id=row.id))
    for row in tempRows:
        row.lnurlpay = req.url_for("temp.api_lnurl_pay", temp_id=row.id)
        row.lnurlwithdraw = req.url_for("temp.api_lnurl_withdraw", temp_id=row.id)
    return tempRows

async def update_temp(temp_id: str, **kwargs) -> Temp:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE tempextension.temp SET {q} WHERE id = ?", (*kwargs.values(), temp_id)
    )
    temp = await get_temp(temp_id)
    assert temp, "Newly updated temp couldn't be retrieved"
    return temp

async def delete_temp(temp_id: str) -> None:
    await db.execute("DELETE FROM tempextension.temp WHERE id = ?", (temp_id,))