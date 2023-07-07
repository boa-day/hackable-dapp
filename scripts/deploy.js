const Neon = require('@cityofzion/neon-js');
const {NeonInvoker} = require("@cityofzion/neon-invoker");
const fs = require('fs');

const deploy = async () => {
  const nefPath = 'boa_day.nef'
  const network = process.argv[2]
  const rpcAddress = network === 'testnet'
    ? NeonInvoker.TESTNET
    : (
      network === 'mainnet'
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

  const nef = Neon.sc.NEF.fromBuffer(fs.readFileSync(nefPath)).serialize()
  const manifest = fs.readFileSync(nefPath.replace('.nef', '.manifest.json')).toString()

  const invoker = await NeonInvoker.init({ rpcAddress, account })
  const resp = await invoker.invokeFunction({
    invocations: [{
      scriptHash: '0xfffdc93764dbaddd97c48f252a53ea4643faa3fd',
      operation: 'deploy',
      args: [
        { type: 'ByteArray', value: nef },
        { type: 'String', value: manifest },
        { type: 'Array', value: [
          { type: 'String', value: privateKey },
          { type: 'ByteArray', value: account.publicKey }
        ] }
      ]
    }],
  })

  console.log('Resp', resp)
}

deploy()