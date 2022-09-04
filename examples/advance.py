from pprint import pprint
from time import sleep

from Crypto.Hash import keccak
from eth_account._utils.legacy_transactions import serializable_unsigned_transaction_from_dict, encode_transaction
from eth_account.datastructures import SignedTransaction
from fireblocks_sdk import FireblocksSDK, MPC_ECDSA_SECP256K1, RAW, \
   TRANSACTION_STATUS_CANCELLED, TRANSACTION_STATUS_FAILED, TRANSACTION_STATUS_COMPLETED, TRANSACTION_STATUS_BLOCKED, \
   TRANSACTION_STATUS_REJECTED
from hexbytes import HexBytes
from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy

apiSecret = open("</path/to/api/key>", 'r').read()
apiKey = '<api user uuid>'

web3 = Web3(Web3.HTTPProvider('https://vilnius.zenithchain.co/http'))

fbks = FireblocksSDK(apiSecret, apiKey)
derPath = "[44,765,<src_vault_id>,0,0]"

# Get source public key
pubkey = fbks.get_public_key_info(algorithm=MPC_ECDSA_SECP256K1, derivation_path=derPath, compressed=False)
keccak = keccak.new(digest_bits=256)
keccak.update(bytes.fromhex(pubkey['publicKey'][2:]))
srcAddr = '0x' + keccak.hexdigest()[-40:]
srcAddr = Web3.toChecksumAddress(srcAddr)

# Get destination public key
pubkey = fbks.get_public_key_info(algorithm=MPC_ECDSA_SECP256K1, derivation_path="[44,765,<dst_vault_id>,0,0]", compressed=False)
keccak = keccak.new(digest_bits=256)
keccak.update(bytes.fromhex(pubkey['publicKey'][2:]))
dstAddr = '0x' + keccak.hexdigest()[-40:]
dstAddr = Web3.toChecksumAddress(dstAddr)

print("Source: " + srcAddr + ", Destination: " + dstAddr)

srcBalance = web3.fromWei(web3.eth.get_balance(srcAddr), 'Ether')
dstBalance = web3.fromWei(web3.eth.get_balance(dstAddr), 'Ether')
print("Source: " + str(srcBalance) + ", Destination: " + str(dstBalance))

web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
nonce = web3.eth.getTransactionCount(srcAddr)
tx = {
   'to': dstAddr,
   'value': web3.toWei(float(srcBalance), 'Ether'),
   'gas': 21000,
   'nonce': nonce,
   'chainId': 81
}
gasPrice = web3.eth.generate_gas_price(tx)
tx['gasPrice'] = gasPrice
tx['value'] = tx['value'] - (21000 * gasPrice)

unsignedTx = serializable_unsigned_transaction_from_dict(tx)
msgToSign = unsignedTx.hash()

extraParams = {
   'rawMessageData': {
       'messages': [
           {
               'content': msgToSign.hex()[2:],
               'derivationPath': [44, 765, <src_vault_id>, 0, 0]
           }
       ],
       'algorithm': MPC_ECDSA_SECP256K1
   }
}

txId = fbks.create_transaction(
   tx_type=RAW,
   extra_parameters=extraParams
)

print("Waiting for: " + str(txId['id']))

txInfo = fbks.get_transaction_by_id(txId['id'])

while (txInfo['status'] not in [TRANSACTION_STATUS_CANCELLED,
                               TRANSACTION_STATUS_REJECTED,
                               TRANSACTION_STATUS_BLOCKED,
                               TRANSACTION_STATUS_COMPLETED,
                               TRANSACTION_STATUS_FAILED]):
   sleep(5)
   txInfo = fbks.get_transaction_by_id(txId['id'])

if txInfo['status'] in [TRANSACTION_STATUS_CANCELLED,
                       TRANSACTION_STATUS_REJECTED,
                       TRANSACTION_STATUS_BLOCKED,
                       TRANSACTION_STATUS_FAILED]:
   print("Failed to sign Tx.")
   pprint(txInfo)
   exit(-1)

sig = txInfo['signedMessages'][0]['signature']
sig["v"] = sig["v"] + 35 + (81 * 2)
encodedTx = encode_transaction(unsignedTx, vrs=(sig["v"], int(sig["r"], 16), int(sig["s"], 16)))
keccak = keccak.new(digest_bits=256)
keccak.update(encodedTx)
signedTx = SignedTransaction(rawTransaction=HexBytes(encodedTx), hash=HexBytes(keccak.digest()), r=int(sig["r"], 16),
                            s=int(sig["s"], 16), v=sig["v"])

transmittedTxHash = web3.eth.sendRawTransaction(signedTx.rawTransaction)

print("Tx Hash: " + str(transmittedTxHash.hex()))