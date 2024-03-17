'''

# seq = [2,5,3,46,7,10]
# print(list(filter(lambda num: num % 2 == 0, seq)))

###

# 1) Get 250, and get 365
stock_info = {'sp500':{'today':300,'yesterday': 250}, 'info':['Time',[24,7,365]]}

print(stock_info['sp500']['yesterday'])
print(stock_info['info'][1][2])


test = "PRICE:345.324:SOURCE--QUANDL"

def source_finder(string):
    price, source = string.split('--')
    return source
   

print(source_finder(test))

# My version one
def price_finder(string):
    string = string.lower()
    try:
        first, second = string.split("price")
        return True
    except Exception:
        return False


# My version two
def price_finder(string):
    string = string.lower()
    if 'price' in string:
        return True
    else:
        return False


# My version three
def price_finder(string):
    string = string.lower()
    return 'price' in string
    

print(price_finder("What is the price?"))
print(price_finder("DUDE, WHAT IS PRICE!!!"))
print(price_finder("The price is 300"))


# My version
def count_price(string):
    string_to_list = []

    for word in string.lower().split():
        string_to_list.append(word)

    return string_to_list.count('price')

# His second version
def count_price(string):
    return string.lower().count('price')
 

price_string = "price the what is the price the price the price"
print(count_price(price_string))


def avg_price(stocks):
    return sum(stocks)/(len(stocks))

print(avg_price([3,4,5]))

'''

import numpy as np 

mylist = [1,2,3]

type(mylist)