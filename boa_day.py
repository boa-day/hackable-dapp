from typing import cast, Any, Optional

from boa3.builtin.compile_time import metadata, public, NeoMetadata
from boa3.builtin.contract import abort
from boa3.builtin.interop import runtime, storage, blockchain
from boa3.builtin.interop.blockchain import Transaction
from boa3.builtin.interop.contract import Contract
from boa3.builtin.nativecontract.contractmanagement import ContractManagement
from boa3.builtin.nativecontract.gas import GAS
from boa3.builtin.nativecontract.stdlib import StdLib
from boa3.builtin.type import helper as type_helper, ECPoint, UInt160


@metadata
def manifest_data() -> NeoMetadata:
    meta_data = NeoMetadata()

    meta_data.name = 'HappyBoaDay'
    meta_data.author = 'COZ'
    meta_data.description = 'https://github.com/boa-day/hackable-dapp'
    meta_data.source = 'https://github.com/boa-day/hackable-dapp'

    return meta_data


@public
def _deploy(data: Any, update: bool):
    if not update:
        set_title('Hack this website using Neo3-Boa. Happy Boa Day!!')
        set_style('text-align: center; line-height: 100vh;')

        container: Transaction = runtime.script_container

        set_admin(container.sender)
        set_authorization(data)
        set_prize_amount(100 * 10 ** 8)


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
    if not is_called_by_boa_contract():
        raise Exception('Not using Neo3-Boa.')

    if not has_authorization():
        raise Exception('Missing some authorization.')

    if not has_prize():
        raise Exception('Someone was faster and already got the prize.')

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


def is_called_by_boa_contract() -> bool:
    contract_hash = runtime.calling_script_hash

    calling: Contract = blockchain.get_contract(contract_hash)
    if calling is None:
        return False

    contract_nef = calling.nef
    compiler = type_helper.to_str(contract_nef[4:68])
    return compiler.startswith('neo3-boa by COZ-1.0.0')


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
    return cast(ECPoint, storage.get(b'\x00\x04'))


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

    storage.put(b'\x00\x04', authorized_pub_key)
    storage.put(b'\x00\x05', priv)


def has_prize() -> bool:
    return get_grand_winner() is None


def get_prize_amount() -> int:
    return type_helper.to_int(storage.get(b'\x00\x06'))


def set_prize_amount(prize_amount: int):
    if prize_amount > 0:
        storage.put(b'\x00\x06', prize_amount)


def give_prize(receiver: UInt160) -> bool:
    return GAS.transfer(runtime.executing_script_hash, receiver, get_prize_amount())


def save_grand_winner(winner: UInt160):
    if get_grand_winner() is not None:
        raise Exception('Prize was already been given')
    storage.put(b'\x00\x07', winner)


def get_grand_winner() -> Optional[UInt160]:
    result = storage.get(b'\x00\x07')
    if isinstance(result, UInt160):
        return result
    return None
