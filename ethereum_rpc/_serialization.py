"""Ethereum RPC schema."""

from collections.abc import Generator, Mapping, Sequence
from types import MappingProxyType, NoneType, UnionType
from typing import Any, TypeVar, Union, cast

from compages import (
    StructureDictIntoDataclass,
    Structurer,
    StructuringError,
    UnstructureDataclassToDict,
    Unstructurer,
    simple_structure,
    simple_typechecked_unstructure,
    structure_into_bool,
    structure_into_int,
    structure_into_list,
    structure_into_none,
    structure_into_str,
    structure_into_tuple,
    structure_into_union,
    unstructure_as_bool,
    unstructure_as_int,
    unstructure_as_list,
    unstructure_as_none,
    unstructure_as_str,
    unstructure_as_tuple,
    unstructure_as_union,
)

from ._rpc import BlockLabel, ErrorCode, Type2Transaction
from ._typed_wrappers import Address, TypedData, TypedQuantity

JSON = None | bool | int | float | str | Sequence["JSON"] | Mapping[str, "JSON"]
"""Values serializable to JSON."""


def _structure_into_bytes(_structurer: Structurer, _structure_into: Any, val: Any) -> bytes:
    if not isinstance(val, str) or not val.startswith("0x"):
        raise StructuringError("The value must be a 0x-prefixed hex-encoded data")
    try:
        return bytes.fromhex(val[2:])
    except ValueError as exc:
        raise StructuringError(str(exc)) from exc


@simple_structure
def _structure_into_block_label(val: Any) -> BlockLabel:
    try:
        return BlockLabel(val)
    except ValueError as exc:
        raise StructuringError(str(exc)) from exc


def _structure_into_typed_data(
    _structurer: Structurer, structure_into: type[TypedData], val: Any
) -> TypedData:
    data = _structure_into_bytes(_structurer, structure_into, val)
    return structure_into(data)


def _structure_into_typed_quantity(
    _structurer: Structurer, structure_into: type[TypedQuantity], val: Any
) -> TypedQuantity:
    if not isinstance(val, str) or not val.startswith("0x"):
        raise StructuringError("The value must be a 0x-prefixed hex-encoded integer")
    int_val = int(val, 0)
    return structure_into(int_val)


def _structure_into_int_common(val: Any) -> int:
    if not isinstance(val, str) or not val.startswith("0x"):
        raise StructuringError("The value must be a 0x-prefixed hex-encoded integer")
    return int(val, 0)


@simple_structure
def _structure_into_int(val: Any) -> int:
    return _structure_into_int_common(val)


def _unstructure_type2tx(
    unstructurer: Unstructurer,
    _unstructure_as: type[Type2Transaction],
    obj: Type2Transaction,
) -> Generator[Type2Transaction, dict[str, JSON], JSON]:
    json = yield obj
    json["type"] = unstructurer.unstructure_as(int, 2)
    return json


@simple_typechecked_unstructure
def _unstructure_typed_quantity(obj: TypedQuantity) -> str:
    return hex(int(obj))


@simple_typechecked_unstructure
def _unstructure_typed_data(obj: TypedData) -> str:
    return "0x" + bytes(obj).hex()


@simple_typechecked_unstructure
def _unstructure_address(obj: Address) -> str:
    return obj.checksum


@simple_typechecked_unstructure
def _unstructure_block_label(obj: BlockLabel) -> str:
    return obj.value


@simple_typechecked_unstructure
def _unstructure_int_to_hex(obj: int) -> str:
    return hex(obj)


@simple_typechecked_unstructure
def _unstructure_bytes_to_hex(obj: bytes) -> str:
    return "0x" + obj.hex()


def _to_camel_case(name: str, _metadata: MappingProxyType[Any, Any]) -> str:
    name = name.removesuffix("_")
    parts = name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


STRUCTURER = Structurer(
    {
        TypedData: _structure_into_typed_data,
        TypedQuantity: _structure_into_typed_quantity,
        ErrorCode: structure_into_int,
        BlockLabel: _structure_into_block_label,
        int: _structure_into_int,
        str: structure_into_str,
        bool: structure_into_bool,
        bytes: _structure_into_bytes,
        list: structure_into_list,
        tuple: structure_into_tuple,
        UnionType: structure_into_union,
        Union: structure_into_union,
        NoneType: structure_into_none,
    },
    [StructureDictIntoDataclass(_to_camel_case)],
)

UNSTRUCTURER = Unstructurer(
    {
        TypedData: _unstructure_typed_data,
        TypedQuantity: _unstructure_typed_quantity,
        Address: _unstructure_address,
        BlockLabel: _unstructure_block_label,
        ErrorCode: unstructure_as_int,
        Type2Transaction: _unstructure_type2tx,
        int: _unstructure_int_to_hex,
        bytes: _unstructure_bytes_to_hex,
        bool: unstructure_as_bool,
        str: unstructure_as_str,
        NoneType: unstructure_as_none,
        list: unstructure_as_list,
        UnionType: unstructure_as_union,
        Union: unstructure_as_union,
        tuple: unstructure_as_tuple,
    },
    [UnstructureDataclassToDict(_to_camel_case)],
)


_T = TypeVar("_T")


def structure(structure_into: type[_T], obj: JSON) -> _T:
    """
    Structures incoming JSON data into the given Ethereum RPC type.
    Raises :py:class:`compages.StructuringError` on failure.
    """
    return STRUCTURER.structure_into(structure_into, obj)


def unstructure(obj: Any, unstructure_as: Any = None) -> JSON:
    """
    Unstructures a given Ethereum RPC entity into a JSON-serializable value.
    Raises :py:class:`compages.UntructuringError` on failure.
    """
    # The result is `JSON` by virtue of the hooks we defined
    return cast("JSON", UNSTRUCTURER.unstructure_as(unstructure_as or type(obj), obj))
