"""Ethereum RPC schema."""

from dataclasses import dataclass
from enum import Enum
from typing import NewType

from ._typed_wrappers import Address, Amount, TypedData


class LogTopic(TypedData):
    """Log topic (32 bytes)."""

    def _length(self) -> int:
        return 32


class BlockHash(TypedData):
    """Block hash (32 bytes)."""

    def _length(self) -> int:
        return 32


class TxHash(TypedData):
    """Transaction hash (32 bytes)."""

    def _length(self) -> int:
        return 32


class TrieHash(TypedData):
    """Trie hash (32 bytes)."""

    def _length(self) -> int:
        return 32


class UnclesHash(TypedData):
    """Hash of block uncles (32 bytes)."""

    def _length(self) -> int:
        return 32


class BlockNonce(TypedData):
    """Block nonce (8 bytes)."""

    def _length(self) -> int:
        return 8


class LogsBloom(TypedData):
    """Bloom filter for logs (256 bytes)."""

    def _length(self) -> int:
        return 256


class BlockLabel(Enum):
    """Block label."""

    LATEST = "latest"
    """The latest mined block."""

    PENDING = "pending"
    """The current pending block."""

    SAFE = "safe"
    """The latest safe head block."""

    FINALIZED = "finalized"
    """The latest finalized block."""

    EARLIEST = "earliest"
    """The earliest/genesis block."""


Block = int | BlockLabel
"""Possible values of the block parameter in RPC calls."""


@dataclass
class TxInfo:
    """Transaction info."""

    chain_id: int

    # TODO: make an enum?
    type_: int
    """Transaction type: 0 for legacy transactions, 2 for EIP1559 transactions."""

    hash_: TxHash
    """Transaction hash."""

    input_: None | bytes
    """The data sent along with the transaction."""

    block_hash: None | BlockHash
    """The hash of the block this transaction belongs to. ``None`` for pending transactions."""

    block_number: int
    """The number of the block this transaction belongs to. May be a pending block."""

    transaction_index: None | int
    """Transaction index. ``None`` for pending transactions."""

    from_: Address
    """Transaction sender."""

    to: None | Address
    """
    Transaction recipient.
    ``None`` when it's a contract creation transaction.
    """

    value: Amount
    """Associated funds."""

    nonce: int
    """Transaction nonce."""

    gas: int
    """Gas used by the transaction."""

    gas_price: Amount
    """Gas price used by the transaction."""

    # TODO: we may want to have a separate derived class for EIP1559 transactions,
    # but for now this will do.

    max_fee_per_gas: None | Amount
    """``maxFeePerGas`` value specified by the sender. Only for EIP1559 transactions."""

    max_priority_fee_per_gas: None | Amount
    """``maxPriorityFeePerGas`` value specified by the sender. Only for EIP1559 transactions."""

    v: int
    """ECDSA recovery id."""

    r: int
    """ECDSA signature r."""

    s: int
    """ECDSA signature s."""


@dataclass
class LogEntry:
    """Log entry metadata."""

    removed: bool
    """
    ``True`` if log was removed, due to a chain reorganization.
    ``False`` if it is a valid log.
    """

    address: Address
    """
    The contract address from which this log originated.
    """

    data: bytes
    """ABI-packed non-indexed arguments of the event."""

    topics: tuple[LogTopic, ...]
    """
    Values of indexed event fields.
    For a named event, the first topic is the event's selector.
    """

    # In the docs of major providers (Infura, Alchemy, Quicknode) it is claimed
    # that the following fields can be null if "it is a pending log".
    # I could not reproduce such behavior, so for now they're staying non-nullable.

    log_index: int
    """Log's position in the block."""

    transaction_index: int
    """Transaction's position in the block."""

    transaction_hash: TxHash
    """Hash of the transactions this log was created from."""

    block_hash: BlockHash
    """Hash of the block where this log was in."""

    block_number: int
    """The block number where this log was."""


@dataclass
class TxReceipt:
    """Transaction receipt."""

    block_hash: BlockHash
    """Hash of the block including this transaction."""

    block_number: int
    """Block number including this transaction."""

    contract_address: None | Address
    """
    If it was a successful deployment transaction,
    contains the address of the deployed contract.
    """

    cumulative_gas_used: int
    """The total amount of gas used when this transaction was executed in the block."""

    effective_gas_price: Amount
    """The actual value per gas deducted from the sender's account."""

    from_: Address
    """Address of the sender."""

    gas_used: int
    """The amount of gas used by the transaction."""

    to: None | Address
    """
    Address of the receiver.
    ``None`` when the transaction is a contract creation transaction.
    """

    transaction_hash: TxHash
    """Hash of the transaction."""

    transaction_index: int
    """Integer of the transaction's index position in the block."""

    # TODO: make an enum?
    type_: int
    """Transaction type: 0 for legacy transactions, 2 for EIP1559 transactions."""

    status: int
    """1 if the transaction was successful, 0 otherwise."""

    logs: tuple[LogEntry, ...]
    """An array of log objects generated by this transaction."""

    logs_bloom: LogsBloom
    """Bloom filter for light clients to quickly retrieve related logs."""

    @property
    def succeeded(self) -> bool:
        """``True`` if the transaction succeeded."""
        return self.status == 1


@dataclass
class BlockInfo:
    """Block info."""

    number: int
    """Block number."""

    hash_: None | BlockHash
    """Block hash. ``None`` for pending blocks."""

    parent_hash: BlockHash
    """Parent block's hash."""

    nonce: None | BlockNonce
    """Block's nonce. ``None`` for pending blocks."""

    miner: None | Address
    """Block's miner. ``None`` for pending blocks."""

    difficulty: int
    """Block's difficulty."""

    total_difficulty: None | int
    """Block's totat difficulty. ``None`` for pending blocks."""

    size: int
    """Block size."""

    gas_limit: int
    """Block's gas limit."""

    gas_used: int
    """Gas used for the block."""

    base_fee_per_gas: Amount
    """Base fee per gas in this block."""

    timestamp: int
    """Block's timestamp."""

    transactions: tuple[TxInfo, ...] | tuple[TxHash, ...]
    """
    A list of transaction hashes in this block, or a list of details of transactions in this block,
    depending on what was requested.
    """

    uncles: tuple[BlockHash, ...]
    """Array of uncle hashes."""

    sha3_uncles: UnclesHash
    """SHA3 of the uncles data in the block."""

    logs_bloom: None | LogsBloom
    """The bloom filter for the logs of the block. ``None`` for pending blocks."""

    transactions_root: TrieHash
    """The root of the transaction trie of the block."""

    state_root: TrieHash
    """The root of the final state trie of the block."""

    receipts_root: TrieHash
    """The root of the receipts trie of the block."""

    extra_data: bytes
    """The "extra data" field of this block."""


class RPCErrorCode(Enum):
    """Standard RPC error codes returned by providers."""

    PARSE_ERROR = -32700
    """
    Invalid JSON was received by the server.
    An error occurred on the server while parsing the JSON text.
    """

    SERVER_ERROR = -32000
    """Reserved for implementation-defined server-errors. See the message for details."""

    INVALID_REQUEST = -32600
    """The JSON sent is not a valid Request object."""

    METHOD_NOT_FOUND = -32601
    """The method does not exist / is not available."""

    INVALID_PARAMETER = -32602
    """Invalid method parameter(s)."""

    INTERNAL_ERROR = -32603
    """Internal JSON-RPC error."""

    EXECUTION_ERROR = 3
    """Contract transaction failed during execution. See the data for details."""


# Need a newtype because unlike all other integers, this one is not hexified on serialization.
ErrorCode = NewType("ErrorCode", int)


@dataclass
class RPCError(Exception):
    """
    A general problem with fulfilling the request at the provider's side.

    This means the provider sent a correct response with an error code
    and possibly some associated data
    (``"error": {"code": ..., "message": ..., "data": ...}`` sub-dictionary in the RPC response).
    """

    code: ErrorCode
    """The error type."""

    message: str
    """The associated message."""

    data: None | bytes = None
    """The associated data (if any)."""

    @property
    def parsed_code(self) -> None | RPCErrorCode:
        """If the error code is known, returns the corresponding enum entry."""
        try:
            return RPCErrorCode(self.code)
        except ValueError:
            return None

    def __str__(self) -> str:
        # Substitute the known code if any, or report the raw integer value otherwise
        code = self.parsed_code or self.code
        return f"RPC error ({code}): {self.message}" + (
            f" (data: {self.data.hex()})" if self.data else ""
        )

    @classmethod
    def with_code(cls, code: RPCErrorCode, message: str, data: None | bytes = None) -> "RPCError":
        """Creates this error given a known error code."""
        return cls(ErrorCode(code.value), message, data=data)


@dataclass
class Type2Transaction:
    """An EIP-1559 (dynamic fee) transaction."""

    # "type": 2
    chain_id: int
    """Chain ID."""

    value: Amount
    """Associated funds."""

    gas: int
    """Gas limit for the transaction."""

    max_fee_per_gas: Amount
    """Maximum total fee the sender is willing to pay."""

    max_priority_fee_per_gas: Amount
    """Maximum miner fee (in addition to the base fee) the sender is willing to pay."""

    nonce: int
    """The transaction nonce."""

    to: None | Address = None
    """The destination of the transaction. ``None`` if it's a deployment transaction."""

    data: None | bytes = None
    """The associated data of the transaction."""


@dataclass
class EthCallParams:
    """Transaction fields for ``eth_call``."""

    to: Address
    """The transaction destination (the contract address)."""

    from_: None | Address = None
    """
    The transaction sender.
    May matter for some contract methods that depend on ``msg.sender``.
    """

    gas: None | int = None
    """
    Gas provided for the transaction execution.
    ``eth_call`` consumes zero gas, but this parameter may be needed by some executions.
    """

    gas_price: None | Amount = None
    """The gas price."""

    value: None | Amount = None
    """The associated funds."""

    data: None | bytes = None
    """The associated data of the transaction."""


@dataclass
class EstimateGasParams:
    """Transaction fields for ``eth_estimateGas``."""

    from_: Address
    """The transaction sender."""

    to: None | Address = None
    """The destination of the transaction. ``None`` if it's a deployment transaction."""

    gas: None | int = None
    """Gas provided for the transaction execution."""

    gas_price: None | Amount = None
    """The gas price."""

    nonce: None | int = None
    """The transaction nonce."""

    value: None | Amount = None
    """The associated funds."""

    data: None | bytes = None
    """The associated data of the transaction."""


@dataclass
class FilterParams:
    """Filter parameters for ``eth_getLogs`` or ``eth_newFilter``."""

    from_block: None | Block = None
    """The starting block of the filter."""

    to_block: None | Block = None
    """The ending block of the filter (inclusive)."""

    address: None | Address | tuple[Address, ...] = None
    """Filter by one or several source addresses."""

    topics: None | tuple[None | LogTopic | tuple[LogTopic, ...], ...] = None
    """Log topics."""


@dataclass
class FilterParamsEIP234:
    """Alternative filter parameters for ``eth_getLogs`` (introduced in EIP-234)."""

    block_hash: BlockHash
    """The hash of the block to which the filter is applied."""

    address: None | Address | tuple[Address, ...] = None
    """Filter by one or several source addresses."""

    topics: None | tuple[None | LogTopic | tuple[LogTopic, ...], ...] = None
    """Log topics."""
