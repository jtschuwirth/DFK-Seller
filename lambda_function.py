from functions.provider import get_provider, get_account
from functions.utils import sellItem, getItemAmount, checkAllowance, addAllowance, getJewelBalance, sendJewel
from functions.data import init_account_table, init_settings_table, init_payouts_table
import json
import time

decimalsJson = open("items_data/decimals.json")
decimals_data = json.load(decimalsJson)
RouterAddress = "0x3C351E1afdd1b1BC44e931E12D4E05D6125eaeCa"
ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)


w3 = get_provider("dfk")

sellables = [
    "DFKGold",
    "Shvas Rune",
    "Moksha Rune",
    "Gaias Tears",
    #"Yellow Pet Egg",
]

def handler(event, context):
    c=1
    account_table = init_account_table()
    payouts_table = init_payouts_table()
    settings_table = init_settings_table()
    gas_buffer = int(settings_table.get_item(Key={"key_": "seller_settings"})["Item"]["min_buffer"])
    accounts = event["users"]
    total_sent = 0
    for user in accounts:
        payout_account = account_table.get_item(Key={"address_": user})["Item"]["pay_to"]
        account = get_account(user, w3)
        nonce = w3.eth.get_transaction_count(account.address)
        print("")
        print(f"{user} ({c}/{len(accounts)})")
        c+=1
        for item in sellables:
            decimals = 0
            amount = getItemAmount(account, item, w3)
            if item in decimals_data:
                decimals = decimals_data[item]
            print(f"{item}: {amount/10**decimals}")
            if checkAllowance(account, item, RouterAddress, ERC20ABI, w3):
                try:
                    addAllowance(account, item, RouterAddress, nonce, ERC20ABI, w3)
                    nonce+=1
                    print(f"Added allowance to {item}")
                except Exception as error:
                    print(f"Error adding allowance to {item}")
                    print(error)

            if amount != 0:
                try:
                    sellItem(account, item, amount, nonce, w3)
                    nonce+=1
                    print(f"Sold {item}")
                except Exception as error:
                    print(f"Error selling {item}")
                    print(error)
            else:
                pass
        balance = getJewelBalance(account, w3)
        print(f"Account has {balance/10**18} Jewel")
        to_send = balance - gas_buffer*10**18
        now = int(time.time())
        try:
            last_payout_time = payouts_table.get_item(Key={"address_": account.address})["Item"]["time_"]
        except:
            last_payout_time = now

        if to_send > 0:
            sendJewel(account, payout_account, to_send, nonce, w3)
            print(f"Sent {to_send/10**18} Jewel to main account")
            total_sent += to_send/10**18
        else:
            print("No jewel to pay")
        
        try:
            payouts_table.delete_item(Key={"address_": account.address})
        except:
            pass

        payouts_table.put_item(Item={
            "address_": account.address,
            "amount_": str(to_send/10**18),
            "time_": str(now),
            "time_delta": str(now - int(last_payout_time)),
        })
        
    print(f"Total sent: {total_sent} Jewel")
    return "Done"