import json
import os

os.chdir('lesson_2') 

# для удобства проверки поставил значения по-умолчанию
def write_order_to_json(item=None, quantity=None, price=None, buyer=None, date=None):
    order_dict = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }

    with open('orders.json') as f:
        date = json.load(f)

    date['orders'].append(order_dict)

    with open('orders.json', 'w') as f:
        json.dump(date, f, indent=4, ensure_ascii=False)
    

write_order_to_json()