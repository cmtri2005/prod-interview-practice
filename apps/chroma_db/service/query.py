from chroma_db import ChromaDBHandler

class Retriever:
    def __init__(self, chroma_handler):
        """
        Khởi tạo bộ truy vấn với handler ChromaDB đã có.
        
        Args:
            chroma_handler (ChromaDBHandler): đối tượng quản lý Chroma DB
        """
        self.chroma_handler = chroma_handler
    
    def search(self, query_embeddings, top_k=5, filters=None):
        """
        Thực hiện truy vấn tìm kiếm tương đồng vector.
        
        Args:
            query_embeddings (list[list[float]]): embedding vector của câu truy vấn
            top_k (int): số lượng kết quả cần trả về
            filters (dict, optional): bộ lọc metadata (filter) nếu muốn áp dụng
            
        Returns:
            list of dict: danh sách kết quả truy vấn có chứa id, document, score, metadata
        """
        # Gọi Chroma query
        results = self.chroma_handler.query(
            query_embeddings=query_embeddings,
            n_results=top_k,
            where=filters
        )
        
        # Xử lý kết quả trả về
        hits = []
        for i in range(len(results['ids'][0])):
            hit = {
                'id': results['ids'][i] if 'ids' in results else None,
                'document': results['documents'][i] if 'documents' in results else None,
                'score': results['distances'][i] if 'distances' in results else None,  # khoảng cách/similarity
                'metadata': results['metadatas'][i] if 'metadatas' in results else None
            }
            hits.append(hit)
        return hits



