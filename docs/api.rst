Public API
==========

.. module:: ethereum_rpc


Schema
------

Primitives
^^^^^^^^^^

.. autoclass:: Amount
   :members:

.. class:: ethereum_rpc._typed_wrappers.CustomAmount

   A type derived from :py:class:`Amount`.

.. autoclass:: Address
   :members:

.. class:: ethereum_rpc._typed_wrappers.CustomAddress

   A type derived from :py:class:`Address`.

.. autoclass:: Block
   :members:

.. autoclass:: BlockLabel
   :members:

.. autoclass:: TxHash
   :members:

.. autoclass:: BlockHash
   :members:

.. autoclass:: LogTopic()

.. autoclass:: TrieHash

.. autoclass:: UnclesHash

.. autoclass:: BlockNonce

.. autoclass:: LogsBloom


Inputs
^^^^^^

.. autoclass:: EthCallParams
   :members:

.. autoclass:: EstimateGasParams
   :members:

.. autoclass:: FilterParams
   :members:

.. autoclass:: FilterParamsEIP234
   :members:

.. autoclass:: Type2Transaction
   :members:


Outputs
^^^^^^^

.. autoclass:: TxReceipt()
   :members:

.. autoclass:: BlockInfo()
   :members:

.. autoclass:: TxInfo()
   :members:

.. autoclass:: LogEntry()
   :members:


EVM
---

.. autoclass:: EVMVersion
   :members:


RPC errors
----------

.. autoclass:: ErrorCode()

.. autoclass:: RPCError
   :show-inheritance:
   :members:

.. autoclass:: RPCErrorCode
   :members:


Serialization
-------------

.. autoclass:: JSON

.. autofunction:: structure

.. autofunction:: unstructure


Keccak
------

.. autofunction:: keccak
