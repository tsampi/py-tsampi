from __future__ import absolute_import

from celery import shared_task
from . import utils

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


# Make a task version of call_chain
call_tsampi_chain = shared_task(utils.call_tsampi_chain)
