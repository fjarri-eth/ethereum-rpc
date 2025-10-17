import os

from ethereum_rpc import (
    BlockHash,
    BlockInfo,
    BlockNonce,
    LogsBloom,
    LogTopic,
    RPCError,
    RPCErrorCode,
    TrieHash,
    TxHash,
    TxInfo,
    TxReceipt,
    UnclesHash,
    structure,
)

EXAMPLE_BLOCK_NO_TX = {
    "baseFeePerGas": "0x7c22a",
    "blobGasUsed": "0xa0000",
    "difficulty": "0x0",
    "excessBlobGas": "0x40000",
    "extraData": "0x726574682f76302e322e302d626574612e362f6c696e7578",
    "gasLimit": "0x1c9c380",
    "gasUsed": "0x15a151f",
    "hash": "0x4600816564332971c25240c7655186ed4dd075b792c1c37f80d03b52d066ead7",
    "logsBloom": (
        "0x"
        "c0490840e4480010626606f82101c0a0915a6060122c0e846460911843f91c04"
        "806c1150860060580213175313ac1d1c4d3262300201e20082e8325d51b59592"
        "2001154704092604073840482d5b8a40b22c1c13cd94600a0c40489388317005"
        "7d24040b4f0e043aa446825c301d88a873e230488c143444012238946ccb060f"
        "41704494420e0310380dc04111260a310c40106f42624024b4a27840054d0682"
        "9a0c37a20950a20ec47d00c09aa094042ac16224340653ca28820209074580b0"
        "130480660d60214cd923200a1a6300f147108b4ac06a02751842dcc46be37151"
        "355a06811485529126102b4812aaef00a45102222a681140ea2501000ab8d200"
    ),
    "miner": "0xc6e2459991bfe27cca6d86722f35da23a1e4cb97",
    "mixHash": "0xa7d82483b13a714db5086781f488c1789c3bc0c04c12bc1788db994e7f5b7de1",
    "nonce": "0x0000000000000000",
    "number": "0x5b50ab",
    "parentBeaconBlockRoot": "0x2093434bba246c55007264bc6c30895f68c4f4d8f10114eaae4b9f01cd3a6d5b",
    "parentHash": "0x0e4040dbadc9d5624d64597f0db228f0bbf6054a4ec83d93dee055124ce7fa1c",
    "receiptsRoot": "0x7da744798ea17da34311389023c8880af257bbabb0aaab1d7b4b63eed1156d92",
    "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
    "size": "0x19d32",
    "stateRoot": "0xfd7a8117c44d10e31bd8dfdcb22020747c492a25fd731e96a95ad9969b5448ec",
    "timestamp": "0x6653bfa4",
    "totalDifficulty": "0x3c656d23029ab0",
    "transactions": [
        "0x5b658410056311f387f92277f59de2c0a6f10f031655f308a63ce18913bafe6b",
        # ... skipped
    ],
    "transactionsRoot": "0xcf80ada30b4f8a33460cdf2f801f9b61a088882cbb5bf62bcbe0f7c377e954a2",
    "uncles": [],
    "withdrawals": [
        {
            "address": "0xf97e180c050e5ab072211ad2c213eb5aee4df134",
            "amount": "0xec0",
            "index": "0x2dab599",
            "validatorIndex": "0x611",
        },
        # ... skipped
    ],
    "withdrawalsRoot": "0x5a34448b2206860290bb5b7402ac72b39660e58221841c8b15eff9d54f21b8c1",
}


EXAMPLE_BLOCK_WITH_TX = {
    "baseFeePerGas": "0x4d737",
    "blobGasUsed": "0x60000",
    "difficulty": "0x0",
    "excessBlobGas": "0x180000",
    "extraData": "0xd883010e00846765746888676f312e32322e32856c696e7578",
    "gasLimit": "0x1c9c380",
    "gasUsed": "0x5cd723",
    "hash": "0x4de55e498118aff378413399d6e6afa4fd87d5e7286f626c5ea8b32e178d1063",
    "logsBloom": (
        "0x"
        "3881981210c045011030060700100060404105001c0010d44000012050930002"
        "00080000320000100c1281c3803640870010024202200a48a3243200400c0402"
        "16025243528412d2501ca60e2000440206411012708890a8182212a041a22034"
        "8a7028022b000226020400c0118209011e6b80c8c80220002210a010cc860012"
        "879020104011012021211010001008800f2840284a081925600150908500c300"
        "000ac4021080289442c02222840024080041437a0c02010008a8d20204620000"
        "d81070620a240006908d00010882002459040348810500020002904200423304"
        "106c200a18801020042490486201acc00a4a0ae00c2094504805130000806804"
    ),
    "miner": "0x9b984d5a03980d8dc0a24506c968465424c81dbe",
    "mixHash": "0x38900f72a7d000243c89942e5b67e466246c04a5cf5adba228e80ec7002f8793",
    "nonce": "0x0000000000000000",
    "number": "0x5b50c8",
    "parentBeaconBlockRoot": "0xafab00b376a09039d8228eaeb66d483467e9564133b81f8e4a87913b0a45348a",
    "parentHash": "0x5182bbad220ad77d8f1ea2ae857f923bb2399a0687f005dbf1bfdc5ca852a793",
    "receiptsRoot": "0x0902e0e708f04ba88e7a4c8d6621565da18bac5f8e56b34017ba124ceb5d1b15",
    "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
    "size": "0xf273",
    "stateRoot": "0x07db744483745ffeb68019b8be833651965bd1c2d6c09e89175b1b217862f0c0",
    "timestamp": "0x6653c118",
    "totalDifficulty": "0x3c656d23029ab0",
    "transactions": [
        {
            "accessList": [],
            "blockHash": "0x4de55e498118aff378413399d6e6afa4fd87d5e7286f626c5ea8b32e178d1063",
            "blockNumber": "0x5b50c8",
            "chainId": "0xaa36a7",
            "from": "0xccbac2bb5bfc98739cbca6456426c3be985a2c8d",
            "gas": "0x545c",
            "gasPrice": "0x3b9fa137",
            "hash": "0x9124c3d0410e50f7c57348e1b004612ff68e9ede6ce7eebf73ae67eaeef5b4e9",
            "input": (
                "0xce27381d00000000006fb67a6976057be3a0bcba17637d35624d32f0bb5d2abe"
                "59815319076eeb954c"
            ),
            "maxFeePerGas": "0xb2d05e00",
            "maxPriorityFeePerGas": "0x3b9aca00",
            "nonce": "0x1b7f",
            "r": "0xd0856cc76ccb130900a6087cfbd588a4f63c52f345246321cfe1051cddeb1cf2",
            "s": "0x63e3181a624dfb621eb47fb09f688c5dd1ad774fc27b6b92ddad6501e15feb87",
            "to": "0x530779a75e54aa9056059409d97693c728301070",
            "transactionIndex": "0x24",
            "type": "0x2",
            "v": "0x0",
            "value": "0x0",
            "yParity": "0x0",
        },
    ],
    "transactionsRoot": "0x362feaffdf9e043632a05faad02395ac62f617f2bf653297aa1272af679c2a2e",
    "uncles": [],
    "withdrawals": [
        {
            "address": "0xf97e180c050e5ab072211ad2c213eb5aee4df134",
            "amount": "0xec0",
            "index": "0x2dab769",
            "validatorIndex": "0x611",
        },
        # ... skipped
    ],
    "withdrawalsRoot": "0xc1754dac84b35fdd3194ad0e903f6ef6e687ec4a60fbc52a605e55f8f18d2db5",
}

EXAMPLE_TX_RECEIPT = {
    "blockHash": "0x50d836c2568df87a67b740c112d3fbc7a5c601d7fe0748496027209e67daa92f",
    "blockNumber": "0x13045ae",
    "contractAddress": None,
    "cumulativeGasUsed": "0x26303b",
    "effectiveGasPrice": "0x31a367fa9",
    "from": "0x6105a6c42e131e791c14bd538895a01645e4573a",
    "gasUsed": "0x316e7",
    "logs": [
        {
            "address": "0x347cc7ede7e5517bd47d20620b2cf1b406edcf07",
            "blockHash": "0x50d836c2568df87a67b740c112d3fbc7a5c601d7fe0748496027209e67daa92f",
            "blockNumber": "0x13045ae",
            "data": "0x000000000000000000000000000000000000000000000000000000006650b913",
            "logIndex": "0x28",
            "removed": False,
            "topics": [
                "0xa38fda88cb3c476adfa74c64be4d74c915b19a3e587e77b887ca804fb9c82c7c",
                "0x000000000000000000000000b0c9f472b2066691ab7fee5b6702c28ab35888b2",
                "0x0000000000000000000000005d2f2668b78a73e30e11e8cd49a377e1ced8ebaf",
                "0x0000000000000000000000000000000000000000000000000000000000000000",
            ],
            "transactionHash": "0x532c4ff510865663772f983477cb35f45c5529624b219c23437a48eb5f9a787f",
            "transactionIndex": "0x36",
        },
        # ... skipped
    ],
    "logsBloom": (
        "0x"
        "0000400040000400000000400000000000000000000040000010000004020102"
        "0000000000000000000000000200000000000000000000000000000000000000"
        "0000000000000000000000020000000000000000000000000800000000000000"
        "0000000002000000000000004000081000000002000000000020000200000000"
        "2000000000000000000000000000000000000000000000040000000000000000"
        "0000000002000000000000000000140200000200000000000100000000000000"
        "0000000000000200000005000000000000000000000000000000000000002000"
        "0000000000000000000000000000000000000000000000000000000000000020"
    ),
    "status": "0x1",
    "to": "0xb0c9f472b2066691ab7fee5b6702c28ab35888b2",
    "transactionHash": "0x532c4ff510865663772f983477cb35f45c5529624b219c23437a48eb5f9a787f",
    "transactionIndex": "0x36",
    "type": "0x2",
}


def test_typed_data_lengths():
    # Just try to create the corresponding types,
    # it will cover their respective length methods.
    # Everything else is in the base class which is tested elsewhere
    TxHash(os.urandom(32))
    BlockHash(os.urandom(32))
    LogTopic(os.urandom(32))
    TrieHash(os.urandom(32))
    UnclesHash(os.urandom(32))
    BlockNonce(os.urandom(8))
    LogsBloom(os.urandom(256))


def test_block_info():
    block = structure(BlockInfo, EXAMPLE_BLOCK_NO_TX)
    assert isinstance(block.transactions[0], TxHash)

    block = structure(BlockInfo, EXAMPLE_BLOCK_WITH_TX)
    assert isinstance(block.transactions[0], TxInfo)


def test_tx_receipt():
    tx = structure(TxReceipt, EXAMPLE_TX_RECEIPT)
    assert tx.succeeded


def test_rpc_error():
    error = RPCError(123, "message")
    assert error.parsed_code is None

    error = RPCError.with_code(RPCErrorCode.INVALID_REQUEST, "message")
    assert error.parsed_code == RPCErrorCode.INVALID_REQUEST
    assert str(error) == "RPC error (RPCErrorCode.INVALID_REQUEST): message"
