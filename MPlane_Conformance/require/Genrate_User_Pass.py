import random, string

def genrate_password():
    a =(random.randint(8, 128))
    pun = '!$%^()_+~{}[].-'
    # get random password pf length 8 with letters, digits, and symbols
    characters = string.ascii_letters + string.digits + pun
    password = ''.join(random.choice(characters) for i in range(a))
    return password

def genrate_username():
    a =(random.randint(3, 23))
    chars = string.digits
    # get random password pf length 8 with letters, digits, and symbols
    username = 'operator{}'.format(''.join(random.choice(chars) for i in range(a)))
    return username  
