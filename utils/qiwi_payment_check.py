import SimpleQIWI
import json
# from data import config


token = "1c63329f05e7af54432640d8ab263cb0"
phone = "79852520741"

min_amount = 10

api = SimpleQIWI.QApi(token=token, phone=phone)

def check_payment(code):
    # checks payments with code and returns amount of donated money
    print("start check")
    api.start()    
    # if api.check(code):
    #     api.stop()
    #     return 1
    # api.stop()
    paym = api.payments
    
    flag = 0
    for p in paym['data']:
        # print(p['comment'])
        if p['comment'] == str(code):
            amount = p['sum']['amount']
            flag=1
            api.stop()
            return amount
    api.stop()
    print("end check")
    return 0
    
    
if __name__ == "__main__":
    
    print(check_payment(578827447))