from boa3.builtin.compile_time import public, metadata, NeoMetadata
from boa3.builtin.type import UInt160

from cpm_out.HackableDApp.contract import HackableDApp


@metadata
def metadata_func() -> NeoMetadata:
    meta = NeoMetadata()

    meta.name = 'TestContract'
    meta.add_permission(contract=HackableDApp.hash)

    return meta


@public(name='changeTitleAndStyle')
def set_title_and_style(title: str, style: str):
    HackableDApp.set_title_and_style(title, style)


@public(name='callGrandPrize')
def grand_prize(receiver: UInt160):
    HackableDApp.grand_prize(receiver)


@public(name='getGrandPrizeValueInGas')
def get_grand_prize_amount_in_gas() -> int:
    return HackableDApp.get_grand_prize_value_in_gas()
