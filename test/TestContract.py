from boa3.builtin.compile_time import public, metadata, NeoMetadata

from cpm_out.HappyBoaDay.contract import HappyBoaDay


@public(name='changeTitleAndStyle')
def set_title_and_style(title: str, style: str):
    HappyBoaDay.set_title_and_style(title, style)


@public(name='callGrandPrize')
def grand_prize():
    HappyBoaDay.grand_prize()


@public(name='getGrandPrizeValueInGas')
def get_grand_prize_amount_in_gas() -> int:
    return HappyBoaDay.get_grand_prize_value_in_gas()
