import json 
import time
from functions.data import chainId

RouterAddress = "0x3C351E1afdd1b1BC44e931E12D4E05D6125eaeCa"
RouterJson = open("abi/UniswapV2Router02.json")
RouterABI = json.load(RouterJson)

itemsJson = open("items_data/items_dfkchain.json")
items = json.load(itemsJson)
decimalsJson = open("items_data/decimals.json")
decimals_data = json.load(decimalsJson)
ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

def sendJewel(account, payout_address, amount, nonce, w3):
    tx = {
        "from": account.address,
        "to": payout_address,
        "value": amount,
        "nonce": nonce,
        "chainId": chainId
    }
    gas = w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = w3.toWei(50, 'gwei')
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)

def getJewelBalance(account, w3):
    return int(w3.eth.get_balance(account.address))

def sellItem(account, item, amount, nonce, w3):
    RouterContract = w3.eth.contract(address=RouterAddress, abi=RouterABI)
    tx = RouterContract.functions.swapExactTokensForETH(
        amount,
        0,
        [items[item], items["Crystal"], items["Jewel"]],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": nonce
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(3, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)

def getItemAmount(account, item, w3):
    contract = w3.eth.contract(address= items[item], abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def checkAllowance(account, item, address, abi, w3):
    contract = w3.eth.contract(address= items[item], abi=abi)
    if int(contract.functions.allowance(account.address, address).call()) == 0:
        return True
    else: 
        return False
    
def addAllowance(account, item, address,  nonce, abi, w3):
    contract = w3.eth.contract(address= items[item], abi=abi)
    tx = contract.functions.approve(address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({
        "from": account.address,
        "nonce": nonce,
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(2, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)