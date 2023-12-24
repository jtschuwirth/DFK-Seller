from decimal import Decimal
import json
import math 
import time

RouterJson = open("abi/UniswapV2Router02.json")
RouterABI = json.load(RouterJson)

itemsJson = open("data/items.json")
items = json.load(itemsJson)

decimalsJson = open("data/decimals.json")
decimals_data = json.load(decimalsJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

contractsJson = open("data/contracts.json")
contracts = json.load(contractsJson)

def sendJewel(account, payout_address, amount, RPCProvider):
    tx = {
        "from": account.address,
        "to": payout_address,
        "value": amount,
        "nonce": account.nonce,
        "chainId": RPCProvider.chainId
    }
    gas = RPCProvider.w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = RPCProvider.w3.to_wei(50, 'gwei')
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)

def getJewelBalance(account, RPCProvider):
    return int(RPCProvider.w3.eth.get_balance(account.address))

def sellItemFromLiquidity(account, amount, token, expected_cost, RPCProvider):
    RouterContract = RPCProvider.w3.eth.contract(address=contracts["RouterAddress"][RPCProvider.chain], abi=RouterABI)
    tx = RouterContract.functions.swapExactTokensForETH(
        amount,
        expected_cost,
        [token.address, items["Jewel"][RPCProvider.chain]],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce
    })
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(3, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)
def getItemAmount(account, item, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= items[item], abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def checkAllowance(account, token, address, abi, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= token.address, abi=abi)
    if int(contract.functions.allowance(account.address, address).call()) == 0:
        return True
    else: 
        return False
    
def addAllowance(account, token, address, abi, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= token.address, abi=abi)
    tx = contract.functions.approve(address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(2, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)

def localGetAmountOut(amountIn, reserves):
    reserve_output = reserves["base_reserve"]
    reserve_input = reserves["token_reserve"]
    return math.floor(((Decimal(amountIn)*Decimal(997) * Decimal(reserve_output)) / (Decimal(reserve_input)*Decimal(1000) + Decimal(amountIn)*Decimal(997)))*Decimal(.99))