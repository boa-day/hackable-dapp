const Neon = require('@cityofzion/neon-js');
const {NeonInvoker} = require("@cityofzion/neon-invoker");
const fs = require('fs');

const deploy = async () => {
  const network = process.argv[2]
  const rpcAddress = network === 'testnet'
    ? NeonInvoker.TESTNET
    : (
      network === 'testnet'
        ? NeonInvoker.MAINNET
        : network
      );
  if (!rpcAddress) throw new Error('Invalid network. Run this script with either "testnet" or "mainnet" as the first argument. Eg.: npm run deploy testnet');

  const privateKey = process.argv[3]
  let account = null

  try {
    account = new Neon.wallet.Account(privateKey)
  } catch (e) {
    throw new Error('Invalid privatekey. Run this script with the privatekey as the second argument. Eg.: npm run deploy testnet abc123')
  }

  const scriptHash = process.argv[4]

  const invoker = await NeonInvoker.init({ rpcAddress, account })
  const resp = await invoker.invokeFunction({
    invocations: [{
      scriptHash: '0xd2a4cff31913016155e38e474a2c06d08be276cf',
      operation: 'transfer',
      args: [
        { type: 'Hash160', value: account.address },
        { type: 'Hash160', value: new Neon.wallet.Account(scriptHash).address },
        { type: 'Integer', value: 100000000 },
        { type: 'Array', value: [] }
      ]
    }],
    signers: [{ scopes: 1 }]
  })

  console.log('Resp', resp)
}

deploy()