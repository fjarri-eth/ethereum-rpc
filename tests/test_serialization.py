import os

import pytest
from compages import StructuringError

from ethereum_rpc import Address, Amount, BlockLabel, Type2Transaction, structure, unstructure
from ethereum_rpc._serialization import TypedData


def test_structure_typed_quantity():
    assert structure(Amount, "0x123") == Amount(0x123)

    with pytest.raises(
        StructuringError, match="The value must be a 0x-prefixed hex-encoded integer"
    ):
        structure(Amount, "abc")


def test_structure_into_int():
    assert structure(int, "0x123") == 0x123

    with pytest.raises(
        StructuringError, match="The value must be a 0x-prefixed hex-encoded integer"
    ):
        structure(int, "abc")


def test_structure_block_label():
    assert structure(BlockLabel, "latest") == BlockLabel.LATEST

    with pytest.raises(StructuringError, match="'abc' is not a valid BlockLabel"):
        structure(BlockLabel, "abc")

    assert unstructure(BlockLabel.LATEST) == "latest"


def test_structure_address():
    address = os.urandom(20)
    assert structure(Address, "0x" + address.hex()) == Address(address)

    with pytest.raises(StructuringError, match="The value must be a 0x-prefixed hex-encoded data"):
        structure(Address, "abc")

    # The error text is weird
    with pytest.raises(
        StructuringError,
        match=r"non-hexadecimal number found in fromhex\(\) arg at position 0",
    ):
        structure(Address, "0xzz")

    assert unstructure(Address(address)) == Address(address).checksum


def test_structure_typed_data():
    class MyData(TypedData):
        def _length(self):
            return 10

    data = os.urandom(10)
    assert structure(MyData, "0x" + data.hex()) == MyData(data)

    with pytest.raises(StructuringError, match="The value must be a 0x-prefixed hex-encoded data"):
        structure(MyData, "abc")

    # The error text is weird
    with pytest.raises(
        StructuringError,
        match=r"non-hexadecimal number found in fromhex\(\) arg at position 0",
    ):
        structure(MyData, "0xzz")

    assert unstructure(MyData(data)) == MyData(data).hex()


def test_structure_type_2_tx():
    tx = Type2Transaction(
        chain_id=0,
        value=Amount.ether(1),
        gas=1234,
        max_fee_per_gas=Amount.wei(10),
        max_priority_fee_per_gas=Amount.wei(20),
        nonce=1,
        to=Address(b"01234567890123456789"),
        data=b"zzz",
    )

    tx_json = {
        "chainId": "0x0",
        "value": "0xde0b6b3a7640000",
        "gas": "0x4d2",
        "maxFeePerGas": "0xa",
        "maxPriorityFeePerGas": "0x14",
        "nonce": "0x1",
        "to": "0x3031323334353637383930313233343536373839",
        "data": "0x7a7a7a",
        "type": "0x2",
    }

    assert unstructure(tx) == tx_json
    assert structure(Type2Transaction, tx_json) == tx
