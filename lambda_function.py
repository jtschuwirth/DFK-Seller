from functions.classes.Account import Account
from functions.classes.RPCProvider import get_rpc_provider
from functions.classes.TablesManager import TablesManager
from functions.getAccount import get_account
from functions.getSecret import get_secret
from functions.sellAllItems import sellAllItems
from functions.utils import getJewelBalance, sendJewel
import json
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

contractsJson = open("data/contracts.json")
contracts = json.load(contractsJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

tablesManager = TablesManager(os.environ["PROD"] == "true")
secret = get_secret(os.environ["PROD"] == "true")
chain = "dfk"

disabled_rpc_list = tablesManager.autoplayer.get_item(Key={"key_": "autoplayer_settings"})["Item"]["disabled_rpc_list"]
RPCProvider = get_rpc_provider(chain, disabled_rpc_list, logger)

def handler(event, context):
    c=1
    gas_buffer = int(tablesManager.autoplayer.get_item(Key={"key_": "seller_settings"})["Item"]["min_buffer"])
    accounts = event["users"]
    total_sent = 0
    for user in accounts:
        payout_address = tablesManager.accounts.get_item(Key={"address_": user})["Item"]["pay_to"]
        account = get_account(tablesManager, secret, user, RPCProvider.w3)
        account = Account(account.key, RPCProvider)
        print("")
        print(f"{user} ({c}/{len(accounts)})")
        c+=1
        sellAllItems(account, RPCProvider)
            
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
                account.update_nonce(RPCProvider)
                sendJewel(account, payout_address, int(to_send*(1-tax/100)), RPCProvider)

                print(f"Sent {to_send*(1-tax/100)/10**18} Jewel to manager")
                total_sent += to_send*(1-tax/100)/10**18

                account.update_nonce(RPCProvider)
                sendJewel(account, tax_receiver_address, int(to_send*(tax/100)), RPCProvider)

                print(f"Sent {to_send*(tax/100)/10**18} Jewel to tax receiver")
                total_sent += to_send*(tax/100)/10**18
        else:
            print("No jewel to pay")
        
        try:
            tablesManager.payouts.delete_item(Key={"address_": account.address})
        except:
            pass

        tablesManager.payouts.put_item(Item={
            "address_": account.address,
            "amount_": str(to_send/10**18),
            "time_": str(now),
            "time_delta": str(now - int(last_payout_time)),
        })
        
    print(f"Total sent: {total_sent} Jewel")
    return "Done"