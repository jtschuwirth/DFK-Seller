from lambda_function import handler

event = {
    "users": [
        "0xEC5fb07Cc8A63114b8E380EA4B8Ca08928872D1F"
    ]
}

print(handler(event, None))