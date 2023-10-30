from typing import List
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from pinecone_text.dense.openai_encoder import OpenAIEncoder
from canopy.knowledge_base.models import KBDocChunk, KBEncodedDocChunk, KBQuery
from canopy.knowledge_base.record_encoder.dense import DenseRecordEncoder
from canopy.models.data_models import Query
from canopy.utils.openai_exceptions import OPEN_AI_TRANSIENT_EXCEPTIONS


class OpenAIRecordEncoder(DenseRecordEncoder):
    """
    OpenAIRecordEncoder is a type DenseRecordEncoder that uses the OpenAI Embeddings endpoints.
    The implementation is based on the Pinecone Text library and the OpenAIEncoder class.
    for more information about the Pinecone Text library see: https://github.com/pinecone-io/pinecone-text

    Note: this implementation is perfroming the same encoding for documents and queries.

    Args:
        model_name: The name of the model to use for encoding.
        batch_size: The number of documents or queries to encode at once.
        Defaults to 1.
        kwargs: Additional arguments to pass to the RecordEncoder.
    """  # noqa: E501

    def __init__(self,
                 *,
                 model_name: str = "text-embedding-ada-002",
                 batch_size: int = 100,
                 **kwargs):
        """
        create an instance of OpenAIEncoder with the given model name.
        initialize the dense encoder.

        Args:
            model_name: The name of the model to use for encoding.
            batch_size: The number of documents or queries to encode at once.
            Defaults to 1.
            kwargs: Additional arguments to pass to the RecordEncoder.
        """  # noqa: E501
        encoder = OpenAIEncoder(model_name)
        super().__init__(dense_encoder=encoder, batch_size=batch_size, **kwargs)

    @retry(
        reraise=True,
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(OPEN_AI_TRANSIENT_EXCEPTIONS),
    )
    def encode_documents(self, documents: List[KBDocChunk]) -> List[KBEncodedDocChunk]:
        """
        Encode a list of documents, takes a list of KBDocChunk and returns a list of KBEncodedDocChunk.

        Args:
            documents: A list of KBDocChunk to encode.

        Returns:
            encoded chunks: A list of KBEncodedDocChunk, where only the values field is populated (and sparse_values is None)
        """  # noqa: E501
        return super().encode_documents(documents)

    async def _aencode_documents_batch(self,
                                       documents: List[KBDocChunk]
                                       ) -> List[KBEncodedDocChunk]:
        raise NotImplementedError

    async def _aencode_queries_batch(self, queries: List[Query]) -> List[KBQuery]:
        raise NotImplementedError
