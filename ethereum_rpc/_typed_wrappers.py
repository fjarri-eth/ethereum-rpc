from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, TypeVar, cast

from ._keccak import keccak

TypedDataLike = TypeVar("TypedDataLike", bound="TypedData")


TypedQuantityLike = TypeVar("TypedQuantityLike", bound="TypedQuantity")


class TypedData(ABC):
    def __init__(self, value: bytes):
        self._value = value
        if not isinstance(value, bytes):
            raise TypeError(
                f"{self.__class__.__name__} must be a bytestring, got {type(value).__name__}"
            )
        if len(value) != self._length():
            raise ValueError(
                f"{self.__class__.__name__} must be {self._length()} bytes long, got {len(value)}"
            )

    @abstractmethod
    def _length(self) -> int:
        """Returns the length of this type's values representation in bytes."""

    def __bytes__(self) -> bytes:
        return self._value

    def __hash__(self) -> int:
        return hash(self._value)

    def hex(self) -> str:
        """Returns the hex form of the data, 0x-prefixed."""
        return "0x" + self._value.hex()

    def _check_type(self: TypedDataLike, other: Any) -> TypedDataLike:
        if type(self) is not type(other):
            raise TypeError(f"Incompatible types: {type(self).__name__} and {type(other).__name__}")
        return cast("TypedDataLike", other)

    def __eq__(self, other: object) -> bool:
        return self._value == self._check_type(other)._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(bytes.fromhex("{self._value.hex()}"))'


class TypedQuantity:
    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                f"{self.__class__.__name__} must be an integer, got {type(value).__name__}"
            )
        if value < 0:
            raise ValueError(f"{self.__class__.__name__} must be non-negative, got {value}")
        self._value = value

    def __hash__(self) -> int:
        return hash(self._value)

    def __int__(self) -> int:
        return self._value

    def _check_type(self: TypedQuantityLike, other: Any) -> TypedQuantityLike:
        if type(self) is not type(other):
            raise TypeError(f"Incompatible types: {type(self).__name__} and {type(other).__name__}")
        return cast("TypedQuantityLike", other)

    def __eq__(self, other: object) -> bool:
        return self._value == self._check_type(other)._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value})"


CustomAmount = TypeVar("CustomAmount", bound="Amount")
"""A subclass of :py:class:`Amount`."""


class Amount(TypedQuantity):
    """
    Represents a sum in the chain's native currency.

    Can be subclassed to represent specific currencies of different networks (ETH, MATIC etc).
    Arithmetic and comparison methods perform strict type checking,
    so currency objects of different types cannot be compared or added to each other.
    """

    def __init__(self, wei: int):
        super().__init__(wei)

    @classmethod
    def wei(cls: type[CustomAmount], value: int) -> CustomAmount:
        """Creates a sum from the amount in wei (``10^(-18)`` of the main unit)."""
        return cls(value)

    @classmethod
    def gwei(cls: type[CustomAmount], value: float) -> CustomAmount:
        """Creates a sum from the amount in gwei (``10^(-9)`` of the main unit)."""
        return cls(int(10**9 * value))

    @classmethod
    def ether(cls: type[CustomAmount], value: float) -> CustomAmount:
        """Creates a sum from the amount in the main currency unit."""
        return cls(int(10**18 * value))

    def as_wei(self) -> int:
        """Returns the amount in wei."""
        return self._value

    def as_gwei(self) -> float:
        """Returns the amount in gwei."""
        return self._value / 10**9

    def as_ether(self) -> float:
        """Returns the amount in the main currency unit."""
        return self._value / 10**18

    def __add__(self: CustomAmount, other: Any) -> CustomAmount:
        return self.wei(self._value + self._check_type(other)._value)

    def __sub__(self: CustomAmount, other: Any) -> CustomAmount:
        return self.wei(self._value - self._check_type(other)._value)

    def __mul__(self: CustomAmount, other: int) -> CustomAmount:
        if not isinstance(other, int):
            raise TypeError(f"Expected an integer, got {type(other).__name__}")
        return self.wei(self._value * other)

    def __floordiv__(self: CustomAmount, other: int) -> CustomAmount:
        if not isinstance(other, int):
            raise TypeError(f"Expected an integer, got {type(other).__name__}")
        return self.wei(self._value // other)

    def __gt__(self, other: Any) -> bool:
        return self._value > self._check_type(other)._value

    def __ge__(self, other: Any) -> bool:
        return self._value >= self._check_type(other)._value

    def __lt__(self, other: Any) -> bool:
        return self._value < self._check_type(other)._value

    def __le__(self, other: Any) -> bool:
        return self._value <= self._check_type(other)._value


CustomAddress = TypeVar("CustomAddress", bound="Address")
"""A subclass of :py:class:`Address`."""


class Address(TypedData):
    """
    Represents an Ethereum address.

    Can be subclassed to represent specific addresses of different networks.
    Comparison methods perform strict type checking,
    so objects of different types cannot be compared to each other.
    """

    def _length(self) -> int:
        return 20

    @classmethod
    def from_hex(cls: type[CustomAddress], address_str: str) -> CustomAddress:
        """
        Creates the address from a hex representation
        (with or without the ``0x`` prefix, checksummed or not).
        """
        return cls(bytes.fromhex(address_str.removeprefix("0x")))

    @cached_property
    def checksum(self) -> str:
        """Retunrs the checksummed hex representation of the address."""
        hex_address = self._value.hex()

        # Because we can't just keccak the address bytes, right? That would be too obvious.
        # But unfortunately that's what the algorithm is, and we have to follow it.
        address_hash = keccak(hex_address.encode("utf-8")).hex()

        return "0x" + "".join(
            (hex_address[i].upper() if int(address_hash[i], 16) > 7 else hex_address[i])
            for i in range(40)
        )

    def __str__(self) -> str:
        return self.checksum

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.from_hex({self.checksum})"
