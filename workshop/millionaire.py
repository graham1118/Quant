from functions import *
import latent_data as ld
from twilio.rest import Client as twClient


price, v_bid, v_ask = get_10s_data()

f = open('stream_data.txt', 'r')
dates = [i.split(',')[0] for i in f.readlines()[-721:]]
latest_time = f.readlines()[-1].split(',')[0]
prices = [i.split(',')[1] for i in f.readlines()[-721:]]
v_bid = f.readlines()[-1].split(',')[2]
v_ask = f.readlines()[-1].split(',')[-1]
f.close()

########################################################
########################################################
passes = 0
for i in range(len(dates)):
    if i > 0 and (abs(dates[i][-2:] - dates[i-1][-2:]) <= 11 or 49 <= abs(dates[i][-2:] - dates[i-1][-2:]) <= 51):
        passes += 1
if passes >= range(len(dates)) - 1:
    trade(prices, v_bid, v_ask, ld.s1, ld.s2, ld.s3, ld.w)

now = datetime.datetime.now()
if now.hour == 16 and now.minute == 20 and 0 < now.second < 10:
    twclient = twClient("ACff230a3271a6423e46668bd8fbda4465", "e078f8b81dfa100e01a2a38a1dccba2c")
    twclient.messages.create(body=latest_time, from_="+115138084714", to="+19196673120").sid
