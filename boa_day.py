from typing import cast, Any, Optional, Union

from boa3.builtin.compile_time import metadata, public, CreateNewEvent, NeoMetadata
from boa3.builtin.contract import abort
from boa3.builtin.interop import blockchain, runtime, storage
from boa3.builtin.interop.contract import call_contract, Contract
from boa3.builtin.interop.iterator import Iterator
from boa3.builtin.nativecontract.contractmanagement import ContractManagement
from boa3.builtin.nativecontract.gas import GAS
from boa3.builtin.nativecontract.stdlib import StdLib
from boa3.builtin.type import helper as type_helper, ECPoint, UInt160


@metadata
def manifest_data() -> NeoMetadata:
    meta_data = NeoMetadata()

    meta_data.name = 'HackableDApp'
    meta_data.author = 'COZ'
    meta_data.description = 'https://github.com/boa-day/hackable-dapp'
    meta_data.source = 'https://github.com/boa-day/hackable-dapp'

    meta_data.supported_standards = ['NEP-11']

    return meta_data


@public
def _deploy(data: Any, update: bool):
    if not update:
        set_title('Hack this website using Neo3-Boa. Happy Boa Day!!')
        set_style('text-align: center; line-height: 100vh;')

        container: blockchain.Transaction = runtime.script_container

        set_admin(container.sender)
        set_authorization(data)
    else:
        set_authorization(data)


@public(name='update')
def update_sc(nef_file: bytes, manifest: bytes, data: Any = None):
    if is_admin():
        ContractManagement.update(nef_file, manifest, data)


@public(name='getTitleAndStyle')
def get_title_and_style() -> str:
    title = get_title()
    style = get_style()

    return StdLib.json_serialize({
        'title': title,
        'style': style
    })


@public(name='setTitleAndStyle')
def set_title_and_style(title: str, style: str):
    if not is_called_by_boa_contract():
        raise Exception('Not using Neo3-Boa.')

    if not isinstance(title, str):
        title = ''
    set_title(title)

    if not isinstance(style, str):
        style = ''
    set_style(style)


@public(name='grandPrize')
def try_to_hack_me(receiver: UInt160):
    if not has_prize():
        raise Exception('Someone was faster and already got the prize.')

    if not is_called_by_boa_contract():
        raise Exception('Not using Neo3-Boa.')

    if not has_authorization():
        raise Exception('Missing some authorization.')

    if not isinstance(receiver, UInt160):
        raise Exception('Incorrect argument type.')

    success = give_prize(receiver)
    if not success:
        raise Exception('Something went wrong with the prize.')

    save_grand_winner(receiver)


@public(name='getGrandPrizeValueInGas')
def get_grand_prize_amount_in_gas() -> int:
    if not has_prize():
        raise Exception('Someone was faster and already got the prize.')

    return get_prize_amount()


@public(name='onNEP17Payment')
def on_nep17_payment(from_address: UInt160, amount: int, data: Any):
    # accept only GAS
    if runtime.calling_script_hash != GAS.hash:
        abort()

    # don't accept anything if grand prize was retrieved
    if not has_prize():
        abort()


@public(name='onNEP11Payment')
def on_nep11_payment(from_address: UInt160, amount: int, token_id: bytes, data: Any):
    # don't accept nfts
    abort()


def is_called_by_boa_contract() -> bool:
    contract_hash = runtime.calling_script_hash

    calling: Contract = blockchain.get_contract(contract_hash)
    if calling is None:
        return False

    contract_nef = calling.nef
    compiler = type_helper.to_str(contract_nef[4:68])
    return compiler.startswith('neo3-boa by COZ-')


def get_title() -> str:
    return type_helper.to_str(storage.get(b'\x00\x01'))


def set_title(new_title: str):
    if len(new_title) > 0:
        storage.put(b'\x00\x01', new_title)


def get_style() -> str:
    return type_helper.to_str(storage.get(b'\x00\x02'))


def set_style(new_style: str):
    if len(new_style) > 0:
        storage.put(b'\x00\x02', new_style)


def is_admin() -> bool:
    return runtime.check_witness(get_admin())


def get_admin() -> UInt160:
    return UInt160(storage.get(b'\x00\x03'))


def set_admin(account: UInt160):
    storage.put(b'\x00\x03', account)


def has_authorization() -> bool:
    return runtime.check_witness(get_authorization())


def get_authorization() -> ECPoint:
    return cast(ECPoint, storage.get(b'publickey'))


def set_authorization(data: Any):
    if not isinstance(data, list):
        raise Exception("Invalid data - not a list")

    data_array: list[bytes] = data
    if len(data_array) != 2:
        raise Exception("Invalid data - incorrect size")

    priv: bytes = data_array[0]
    if not isinstance(priv, bytes):
        raise Exception("Invalid data")
    authorized_pub_key = ECPoint(data_array[1])

    storage.put(b'publickey', authorized_pub_key)
    storage.put(b'private', priv)
    storage.put(b'source', 'https://github.com/boa-day/hackable-dapp')


def has_prize() -> bool:
    return get_grand_winner() is None


def get_prize_amount() -> int:
    return GAS.balanceOf(runtime.executing_script_hash)


def give_prize(receiver: UInt160) -> bool:
    prize = get_prize_amount()
    if prize <= 0:
        # missing contract configuration
        return False

    success = GAS.transfer(runtime.executing_script_hash, receiver, prize)
    if success:
        mint_prize_token(receiver)

    return success


def save_grand_winner(winner: UInt160):
    if get_grand_winner() is not None:
        raise Exception('Prize was already been given')
    storage.put(b'\x00\x04', winner)


def get_grand_winner() -> Optional[UInt160]:
    result = storage.get(b'\x00\x04')
    if isinstance(result, UInt160):
        return result
    return None


TOKEN_SYMBOL = 'HACK'
TOKEN_DECIMALS = 0


SUPPLY_KEY = b'\x01\x01'
BALANCE_PREFIX = b'\x01\x02'
TOKENS_OF_ACCOUNT_PREFIX = b'\x01\x03'
TOKEN_PREFIX = b'\x01\x04'
PROPERTIES_PREFIX = b'\x01\x05'


on_transfer = CreateNewEvent(
    [
        ('from_addr', Union[UInt160, None]),
        ('to_addr', Union[UInt160, None]),
        ('amount', int),
        ('token_id', bytes)
    ],
    'Transfer'
)


@public(safe=True)
def symbol() -> str:
    return TOKEN_SYMBOL


@public(safe=True)
def decimals() -> int:
    return TOKEN_DECIMALS


@public(name='totalSupply', safe=True)
def total_supply() -> int:
    return type_helper.to_int(storage.get(SUPPLY_KEY, storage.get_read_only_context()))


@public(name='balanceOf', safe=True)
def balance_of(owner: UInt160) -> int:
    return type_helper.to_int(storage.get(get_balance_key(owner), storage.get_read_only_context()))


@public(name='tokensOf', safe=True)
def tokens_of(owner: UInt160) -> Iterator:
    flags = storage.FindOptions.REMOVE_PREFIX | storage.FindOptions.KEYS_ONLY
    context = storage.get_read_only_context()
    return storage.find(get_tokens_of_key(owner), context, flags)


@public
def transfer(to: UInt160, token_id: bytes, data: Any) -> bool:
    assert isinstance(to, UInt160)

    token_owner = get_owner_of(token_id)
    if not runtime.check_witness(token_owner):
        return False

    if token_owner != to:
        from_balance_key = get_balance_key(token_owner)
        old_balance_owner = balance_of(token_owner)
        storage.put(from_balance_key, old_balance_owner - 1)

        to_balance_key = get_balance_key(to)
        old_balance_to = balance_of(to)
        storage.put(to_balance_key, old_balance_to + 1)

        from_tokens_key = get_tokens_of_key(token_owner)
        to_tokens_key = get_tokens_of_key(to)

        storage.delete(from_tokens_key)
        storage.put(to_tokens_key, token_id)
        storage.put(get_token_owner_key(token_id), to)

    post_transfer(token_owner, to, token_id, data)
    return True


def post_transfer(token_owner: Union[UInt160, None], to: Union[UInt160, None], token_id: bytes, data: Any):
    on_transfer(token_owner, to, 1, token_id)
    if to is not None:
        contract = blockchain.get_contract(to)
        if contract is not None:
            call_contract(to, 'onNEP11Payment', [token_owner, 1, token_id, data])


@public(name='ownerOf', safe=True)
def owner_of(token_id: bytes) -> UInt160:
    return get_owner_of(token_id)


@public(safe=True)
def tokens() -> Iterator:
    flags = storage.FindOptions.REMOVE_PREFIX | storage.FindOptions.KEYS_ONLY
    context = storage.get_read_only_context()
    return storage.find(TOKEN_PREFIX, context, flags)


@public(safe=True)
def properties(token_id: bytes) -> dict:
    token_prop = get_properties_serialized(token_id)
    assert len(token_prop) > 0
    token_prop_json: dict = StdLib.json_deserialize(type_helper.to_str(token_prop))
    return token_prop_json


def mint_prize_token(token_owner: UInt160) -> bytes:
    token_id = total_supply() + 1
    token_id_bytes = type_helper.to_bytes(token_id)

    storage.put(get_token_owner_key(token_id_bytes), token_owner)
    storage.put(get_tokens_of_key(token_owner), token_id_bytes)

    balance_key = get_balance_key(token_owner)
    old_balance = balance_of(token_owner)
    storage.put(balance_key, old_balance + 1)

    storage.put(SUPPLY_KEY, token_id)

    token_properties = {
        'name': 'Certified Hacker',
        'description': 'Winner of Boa Day Hack Competition',
        'image': 'https://coz.io/hackabledapp.png'
    }
    storage.put(get_token_properties_key(token_id_bytes), StdLib.json_serialize(token_properties))

    post_transfer(None, token_owner, token_id_bytes, None)
    return token_id_bytes


def get_owner_of(token_id: bytes) -> UInt160:
    owner = storage.get(get_token_owner_key(token_id), storage.get_read_only_context())
    return UInt160(owner)


def get_properties_serialized(token_id: bytes) -> bytes:
    return storage.get(get_token_properties_key(token_id), storage.get_read_only_context())


def get_tokens_of_key(address: UInt160) -> bytes:
    return TOKENS_OF_ACCOUNT_PREFIX + address


def get_balance_key(address: UInt160) -> bytes:
    return BALANCE_PREFIX + address


def get_token_owner_key(token_id: bytes) -> bytes:
    return TOKEN_PREFIX + token_id


def get_token_properties_key(token_id: bytes) -> bytes:
    return PROPERTIES_PREFIX + token_id
