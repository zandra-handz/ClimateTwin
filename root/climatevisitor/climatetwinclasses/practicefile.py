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

'''

mylist = [1,2,3]

print(type(mylist))

print(np.array(mylist))

myarr = np.array(mylist)
print(type(myarr))
# = numpy.ndarray

my_matrix = [[1,2,3],[4,5,6],[7,8,9]]

print(my_matrix)

print(np.array(my_matrix))

print(np.arange(0, 10, 2))


# print(np.zeros(5))

# print(np.zeros((5,5)))

# print(np.ones((4,4)))

print(np.linspace(0,10,11))

# Identity matrix (always known as a square matrix with a 1 along the diagonal)
print(np.eye(5))

# 'uniformly' = all numbers have same likelihood

print(np.random.rand(1))
print('')
print('Random rows and columns:')
print(np.random.rand(5,6))

print('')
print('Standard normal distribution:')
#mean is at 0 and variance of 1
#values closer to 0 more likely to appear than those farther away from 0
print(np.random.randn(10)) 
print(np.random.randn(2,3))
print('')

print('Random int:')
print(np.random.randint(0,101,5))
print('')

print('Random int as a matrix:')
print(np.random.randint(0,101,(4,5)))
print('')


# seed = random set that can be reused
np.random.seed(42)
print(np.random.rand(4))

arr = np.arange(0,25)
print(arr)
print(arr.reshape(5,5))
print(arr)

ranarr = np.random.randint(0,101,10)

print(ranarr)

print(ranarr.max())

print(ranarr.min())

#index location
print(ranarr.argmax())
print(ranarr.argmin())


print(ranarr.dtype)


print(arr.shape)

print(arr.reshape(5,5))
print(arr.reshape(25,1))
print(arr.reshape(1,25))
'''

arr = np.arange(0,11)
