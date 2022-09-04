const fs = require('fs');
const path = require('path');
const {FireblocksSDK, PeerType, TransactionOperation, TransactionStatus} = require('fireblocks-sdk');
const { exit } = require('process');
const {sha256} = require('js-sha256');
const { inspect } = require('util');
 
const apiSecret = fs.readFileSync(path.resolve("</path/to/api/key>"), "utf8");
const apiKey = "<api user uuid>";
const fbks = new FireblocksSDK(apiSecret, apiKey);
 
const eip_message = {
   "types": {
       "example_eip712": [
           {
               "name": "value",
               "type": "string"
           }
       ],
       "EIP712Domain": [
           {
               "name": "name",
               "type": "string"
           },
           {
               "name": "version",
               "type": "string"
           },
           {
               "name": "chainId",
               "type": "uint256"
           }
       ]
   },
   "domain": {
       "name": "example_eip712",
       "chainId": 1,
       "version": "1.0"
   },
   "message": {
       "value": "test 123123"
   },
   "primaryType": "example_eip712"
};
 
(async() => {
  
   let {id} = await fbks.createTransaction({
       source:{
           type: PeerType.VAULT_ACCOUNT,
           id: '2'
       },
       assetId: 'ETH_TEST',
       operation: TransactionOperation.TYPED_MESSAGE,
       extraParameters:{
           rawMessageData:{
               messages: [
                   {
                       content: Buffer.from('test').toString('hex'),
                       index: 0,
                       type: 'ETH_MESSAGE'
                       // To use EIP712, uncomment the below 3 lines and comment out the above 3 lines (until including content).
                       // content: eip_message,
                       // index: 0,
                       // type: 'EIP712'
                   }
               ]
           }
       }
   });
   let tx = await fbks.getTransactionById(id);
   while(! [TransactionStatus.BLOCKED, TransactionStatus.REJECTED, TransactionStatus.COMPLETED, TransactionStatus.CANCELLED, TransactionStatus.FAILED].includes(tx.status)){
       await new Promise(r => setTimeout(r, 5000));
       tx = await fbks.getTransactionById(id);
   }
 
   if([TransactionStatus.BLOCKED, TransactionStatus.REJECTED, TransactionStatus.CANCELLED, TransactionStatus.FAILED].includes(tx.status)){
       throw `Transaction failed - ${inspect(tx, false, null, true)}`
   }
 
   console.log(`Signed Message: ${inspect(tx.signedMessages, false, null, true)}`);
 
})().catch((e)=>{console.log('Error: ', e);exit(-1)});

