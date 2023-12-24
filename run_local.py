from lambda_function import handler

event = {
    "users": [
        "0x0E4a21031182fE25D763229ed4ADB90A8eC8bD7B",
        #"0x17765249F934ceC90E6BC2C9AF8376Ece0bA19Ef",
        #"0x99B85C17DbD5994A53A4f6fEE40Bf4958b455f04",
        #"0xe486Eadd11eC0b832CD3F3740AdB2D6551e8fD6E",
        #"0xfe865281921108e00358ad156Af620dF73524c2c",
        #"0xf9f0c9a18fCBE59ffD49767a27E1F5956Bf5b3f6"
    ]
}

print(handler(event, None))