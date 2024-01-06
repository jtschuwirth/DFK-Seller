from functions.classes.APIService import APIService
from functions.classes.Account import Account, get_account
from functions.classes.RPCProvider import get_rpc_provider
from functions.classes.Secret import get_secret
from functions.classes.TablesManager import TablesManager
from functions.sellAllItems import sellAllItems
from functions.utils import getJewelBalance, sendJewel
from functions.classes.Config import isProd, secretName
import json
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)


def handler(event, context):
    chain = "dfk"
    tablesManager = TablesManager(isProd)
    apiService = APIService(chain)

    secret = get_secret(secretName)
    RPCProvider = get_rpc_provider(chain, [], logger)
    c=1
    gas_buffer = int(tablesManager.autoplayer.get_item(Key={"key_": "seller_settings"})["Item"]["min_buffer"])
    accounts = event["users"]
    total_sent = 0
    for user in accounts:
        payout_address = tablesManager.accounts.get_item(Key={"address_": user})["Item"]["pay_to"]
        account = get_account(tablesManager, secret, user, RPCProvider)
        print("")
        print(f"{user} ({c}/{len(accounts)})")
        c+=1
        sellAllItems(account, apiService, RPCProvider)
            
        balance = getJewelBalance(account, RPCProvider)
        print(f"Account has {balance/10**18} Jewel")
        to_send = balance - gas_buffer*10**18
        now = int(time.time())
        try:
            last_payout_time = tablesManager.payouts.get_item(Key={"address_": account.address})["Item"]["time_"]
        except:
            last_payout_time = now

        tax = tablesManager.managers.get_item(Key={"address_": payout_address})["Item"]["tax"]
        tax_receiver_address = tablesManager.autoplayer.get_item(Key={"key_": "seller_settings"})["Item"]["tax_receiver"]
        if to_send > 0:
            if tax == 0:
                account.update_nonce(RPCProvider)
                sendJewel(account, payout_address, to_send, RPCProvider)

                print(f"Sent {to_send/10**18} Jewel to manager")
                total_sent += to_send/10**18
            else:
                tax = to_send*(1-tax/100)
                to_send = to_send*(1-(tax/100))

                account.update_nonce(RPCProvider)
                sendJewel(account, payout_address, int(tax), RPCProvider)

                print(f"Sent {tax/10**18} Jewel to manager")
                total_sent += tax/10**18

                account.update_nonce(RPCProvider)
                sendJewel(account, tax_receiver_address, int(to_send), RPCProvider)

                print(f"Sent {to_send/10**18} Jewel to tax receiver")
                total_sent += to_send/10**18

                tablesManager.autoplayer_fee.put_item(Item={
                    "address_": account.address,
                    "payout_address": tax_receiver_address,
                    "amount_": str(int(tax/10**18)),
                    "time_": str(now),
                    "time_delta": str(now - int(last_payout_time)),
                })
        else:
            print("No jewel to pay")
        
        try:
            tablesManager.payouts.delete_item(Key={"address_": account.address})
        except:
            pass

        tablesManager.payouts.put_item(Item={
            "address_": account.address,
            "payout_address": payout_address,
            "amount_": str(to_send/10**18),
            "time_": str(now),
            "time_delta": str(now - int(last_payout_time)),
        })
        
    print(f"Total sent: {total_sent} Jewel")
    return "Done"