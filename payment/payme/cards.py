from pprint import pprint

from payme.cards.subscribe_cards import PaymeSubscribeCards
from payme.receipts.subscribe_receipts import PaymeSubscribeReceipts
from environs import Env

import os
import sys


env = Env()
env.read_env()


client = PaymeSubscribeCards(
    base_url =  'https://checkout.test.paycom.uz/api',
    paycom_id = '5e730e8e0b852a417aa49ceb'
)


payment = PaymeSubscribeReceipts(
    base_url =  'https://checkout.test.paycom.uz/api',
    paycom_id = '5e730e8e0b852a417aa49ceb',
    paycom_key = 'ZPDODSiTYKuX0jyO7Kl2to4rQbNwG08jbghj'
)



class PaymeSubscribeCardsCreate:
    
    def create_card(self,number,expire,save=True):
        resp = client.cards_create(number=number, expire=expire,save=save)
        return resp['result']['card']['token']
    
    def get_verify_code_card(self,token):
        resp = client.card_get_verify_code(token = token)
        return resp
    
    def verify_card(self,token,code):
        resp = client.cards_verify(verify_code=code, token=token)
        return resp
    
    def check_card(self,token):
        resp = client.cards_check(token=token)
        return resp
    
    def remove_card(self,token):
        resp = client.cards_remove(token=token)
        return resp
