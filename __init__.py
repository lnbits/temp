import asyncio

from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart

db = Database("ext_tempextension")

temp_ext: APIRouter = APIRouter(
    prefix="/temp", tags=["Temp"]
)

temp_static_files = [
    {
        "path": "/temp/static",
        "name": "temp_static",
    }
]

def temp_renderer():
    return template_renderer(["temp/templates"])

from .lnurl import *
from .tasks import wait_for_paid_invoices
from .views import *
from .views_api import *


def temp_start():
    loop = asyncio.get_event_loop()
    loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))