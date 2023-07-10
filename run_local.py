from lambda_function import handler

event = {
    "users": [
        "0xfd768E668A158C173e9549d1632902C2A4363178",
        "0xD9e0068b012bE03501EF981b24d3dBEba3aa826d"
    ]
}

print(handler(event, None))