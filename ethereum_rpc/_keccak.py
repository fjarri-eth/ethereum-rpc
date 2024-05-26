"""
Due to a number of unfortunate design choices, namely:
- Ethereum picking keccak instead of the standard SHA3
- Python deciding not to include keccak in the standard library
- Ethereum providers requiring checksummed addresses
- Checksum calculation using keccak
... keccak is a part of the Ethereum API. So it has to be a part of this package.
"""

from Crypto.Hash import keccak as pycryptodome_keccak


def keccak(data: bytes) -> bytes:
    """Calculates Keccak-256 hash of the given data."""
    return pycryptodome_keccak.new(data=data, digest_bits=256).digest()
