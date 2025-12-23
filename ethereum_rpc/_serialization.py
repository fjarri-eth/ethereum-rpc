"""Ethereum RPC schema."""

from collections.abc import Generator, Mapping, Sequence
from types import NoneType, UnionType
from typing import Any, TypeVar, Union, cast

from compages import (
    AsBool,
    AsDataclassToDict,
    AsInt,
    AsList,
    AsNone,
    AsStr,
    AsTuple,
    AsUnion,
    DataclassBase,
    IntoBool,
    IntoDataclassFromMapping,
    IntoInt,
    IntoList,
    IntoNone,
    IntoStr,
    IntoTuple,
    IntoUnion,
    StructLikeOptions,
    StructureHandler,
    Structurer,
    StructurerContext,
    StructuringError,
    UnstructureHandler,
    Unstructurer,
    UnstructurerContext,
)

from ._rpc import BlockLabel, ErrorCode, Type2Transaction
from ._typed_wrappers import Address, TypedData, TypedQuantity

JSON = None | bool | int | float | str | Sequence["JSON"] | Mapping[str, "JSON"]
"""Values serializable to JSON."""


class _IntoBytesFromHex(StructureHandler):
    def structure(self, _context: StructurerContext, val: Any) -> bytes:
        if not isinstance(val, str) or not val.startswith("0x"):
            raise StructuringError("The value must be a 0x-prefixed hex-encoded data")
        try:
            return bytes.fromhex(val[2:])
        except ValueError as exc:
            raise StructuringError(str(exc)) from exc


class _IntoBlockLabel(StructureHandler):
    def structure(self, _context: StructurerContext, val: Any) -> BlockLabel:
        try:
            return BlockLabel(val)
        except ValueError as exc:
            raise StructuringError(str(exc)) from exc


class _IntoTypedData(StructureHandler):
    def structure(self, context: StructurerContext, val: Any) -> TypedData:
        data = _IntoBytesFromHex().structure(context, val)
        # Can cast here because we are attaching this handler to `TypedData`,
        # and it is not exported.
        structure_into = cast("type[TypedData]", context.structure_into)
        return structure_into(data)


class _IntoTypedQuantity(StructureHandler):
    def structure(self, context: StructurerContext, val: Any) -> TypedQuantity:
        int_val = _IntoIntFromHex().structure(context, val)
        # Can cast here because we are attaching this handler to `TypedQuantity`,
        # and it is not exported.
        structure_into = cast("type[TypedQuantity]", context.structure_into)
        return structure_into(int_val)


class _IntoIntFromHex(StructureHandler):
    def structure(self, _context: StructurerContext, val: Any) -> int:
        if not isinstance(val, str) or not val.startswith("0x"):
            raise StructuringError("The value must be a 0x-prefixed hex-encoded integer")
        return int(val, 0)


class _IntoTypedTx(StructureHandler):
    def __init__(self, type_num: int):
        self._type_num = type_num

    def structure(
        self, context: StructurerContext, val: Any
    ) -> Generator[Any, dict[str, JSON], JSON]:
        if not isinstance(val, Mapping):
            raise StructuringError("Transaction must be a mapping type")
        if "type" not in val:
            raise StructuringError("Transaction is missing the `type` field")
        tx_type = context.structurer.structure_into(int, val.get("type"))
        if tx_type != self._type_num:
            raise StructuringError(f"Expected transaction type {self._type_num}, got {tx_type}")
        tx = yield val
        return tx


class _AsTypedTx(UnstructureHandler):
    def __init__(self, type_num: int):
        self._type_num = type_num

    def unstructure(
        self, context: UnstructurerContext, val: Any
    ) -> Generator[Any, dict[str, JSON], JSON]:
        tx_dict = yield val
        tx_dict["type"] = _AsIntToHex().unstructure(context, self._type_num)
        return tx_dict


class _AsTypedQuantity(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: TypedQuantity) -> str:
        return hex(int(val))


class _AsTypedData(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: TypedData) -> str:
        return "0x" + bytes(val).hex()


class _AsAddress(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: Address) -> str:
        return val.checksum


class _AsBlockLabel(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: BlockLabel) -> str:
        return val.value


class _AsIntToHex(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: int) -> str:
        return hex(val)


class _AsBytesToHex(UnstructureHandler):
    def unstructure(self, _context: UnstructurerContext, val: bytes) -> str:
        return "0x" + val.hex()


def _to_camel_case(name: str, _metadata: Any) -> str:
    name = name.removesuffix("_")
    parts = name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


STRUCTURER = Structurer(
    {
        TypedData: _IntoTypedData(),
        TypedQuantity: _IntoTypedQuantity(),
        ErrorCode: IntoInt(),
        BlockLabel: _IntoBlockLabel(),
        Type2Transaction: _IntoTypedTx(2),
        int: _IntoIntFromHex(),
        str: IntoStr(),
        bool: IntoBool(),
        bytes: _IntoBytesFromHex(),
        list: IntoList(),
        tuple: IntoTuple(),
        UnionType: IntoUnion(),
        Union: IntoUnion(),
        NoneType: IntoNone(),
        DataclassBase: IntoDataclassFromMapping(
            StructLikeOptions(to_unstructured_name=_to_camel_case)
        ),
    },
)

UNSTRUCTURER = Unstructurer(
    {
        TypedData: _AsTypedData(),
        TypedQuantity: _AsTypedQuantity(),
        Address: _AsAddress(),
        BlockLabel: _AsBlockLabel(),
        ErrorCode: AsInt(),
        Type2Transaction: _AsTypedTx(2),
        int: _AsIntToHex(),
        bytes: _AsBytesToHex(),
        bool: AsBool(),
        str: AsStr(),
        NoneType: AsNone(),
        list: AsList(),
        UnionType: AsUnion(),
        Union: AsUnion(),
        tuple: AsTuple(),
        DataclassBase: AsDataclassToDict(StructLikeOptions(to_unstructured_name=_to_camel_case)),
    },
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
