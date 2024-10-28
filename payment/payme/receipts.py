from pprint import pprint

from payme.cards.subscribe_cards import PaymeSubscribeCards
from payme.receipts.subscribe_receipts import PaymeSubscribeReceipts
from environs import Env

import os
import sys

env = Env()
env.read_env()


payment = PaymeSubscribeReceipts(
    base_url =  'https://checkout.paycom.uz',
    paycom_id = '64aa4e53d2cbaa16838e2023',
    paycom_key = 'iSGgeUF1k%Zg&y8h6E4SzOYFu6VVEXFF@W9h'
)


