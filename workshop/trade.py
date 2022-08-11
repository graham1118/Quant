from web3 import Web3
from tokens import *
import json
import time
import requests


metamask = '0xF396142EBf3edd1099fD20aa31575D66A2d6DccA'
web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mainnet')) #/mumbai for testnet


def get_price(amountIn, path):
	#initialize web3 node
	web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mainnet'))
	
	router_address = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
	factory_address ='0xc35DADB65012eC5796536bD9864eD8773aBc74C4'
	
	#retrieve smart contracts
	router = web3.eth.contract(address = router_address, abi = router_abi)
	factory = web3.eth.contract(address = factory_address, abi = factory_abi)
	
	#call method in smart contract to get token pair address
	pair_address = factory.functions.getPair(token[path[0]]['cksum_address'], token[path[1]]['cksum_address']).call()

	#use pair address to get smart contract for that pair --> get amount of each token in liquidity pool (reserves)
	exchange = web3.eth.contract(address = pair_address, abi = token_abi)
	reserves = exchange.functions.getReserves().call()
	
	#use reserves to get price of asset
	price = router.functions.quote(amountIn*10**token[path[0]]['decimals'], reserves[0], reserves[1]).call()
	return price


def get_balance(blockchain, wallet=None):
	
	if blockchain = 'mainnet':
		web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mainnet')) #/mumbai for testnet
	if blockchain = 'testnet':
		web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mumbai'))

	#get usdt balance --> 1) initialize contract 2) call contract method 3) convert from uint to int
	USDT_contract = web3.eth.contract(address=USDT, abi=token_abi)
	USDT_balance = USDT_contract.functions.balanceOf(wallet).call()
	USDT_balance = USDT_balance/10**6
	
	#wbtc balance
	WBTC_contract = web3.eth.contract(address=WBTC, abi=token_abi)
	WBTC_balance = WBTC_contract.functions.balanceOf(wallet).call()
	WBTC_balance = WBTC_balance/10**8

	#matic balance
	MATIC_balance = web3.eth.get_balance(wallet)/10**token['MATIC']['decimals']
	return {'WBTC':WBTC_balance, 'USDT':USDT_balance, 'MATIC':MATIC_balance}


def approvePath(web3,ERC20,path,amounts,spender):
    '''
    Sets approval for spender to transfer callers tokens
    Parameters
    ----------
    path: path of tokens that need approval for trade or deposit
    amounts: amount of tokens that need approval
    spender: Address to transfer tokens
    Returns
    -------
    Returns the path of the addresses in checksum
    '''
    gas_data = requests.get('https://gasstation-mainnet.matic.network').json()	
    gas = gas_data['fast']
    router_address = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'

    list_of_rec = []
    for i in range(len(path)):
        TokenA = contractInstance(web3,ERC20,path[i])
        t = TokenA.encodeABI(fn_name='approve',args=[router_address,amounts[i]])
        tx = {'chainId': 137,
        	  'from':metamask,
              'nonce':web3.eth.getTransactionCount(metamask),
              'data':t,
              'to':path[i],
              'gas':21000 * 10,
              'gasPrice':web3.toWei(int(gas),'gwei')
              }        
        
        r = functiontransaction(web3, key, tx)
        list_of_rec.append(r)
    return list_of_rec

#swap(get_balance(wallet = '0x'), [USDT, WBTC])
def swap(amountIn, path, blockchain):
	gas_data = requests.get('https://gasstation-mainnet.matic.network').json()	
	gas = gas_data['fast']
	metamask = '0xF396142EBf3edd1099fD20aa31575D66A2d6DccA'
	
	amountOutMin = get_price(amountIn, path)
	amountIn = amountIn*10**token[path[0]]['decimals']

	if blockchain = 'mainnet':
		web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mainnet')) #/mumbai for testnet
	if blockchain = 'testnet':
		web3 = Web3(Web3.HTTPProvider('https://speedy-nodes-nyc.moralis.io/f67bfd109a69698191dc9597/polygon/mumbai'))


	router_address = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
	router = contractInstance(web3,router_abi,router_address)
	
	#approvePath(web3,IERC20,[path[0]],[amountIn],router_address)
	rece = router.encodeABI(fn_name='swapExactTokensForTokens',args=[amountIn, 10, path, metamask, int(time.time()) + 10])
	
	tx = {'chainId':137,
		'from':metamask,
		'nonce':web3.eth.getTransactionCount(metamask),
		'data':rece,
		'to':router_address,
		'gas':21000 * 10,
		'gasPrice':web3.toWei(int(gas),'gwei')}

	return functiontransaction(web3,key,tx)