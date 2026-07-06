from app.domain.documents.schemas import DocumentChunk


class ChunkingService:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        if overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk_document(
        self,
        document_id: str,
        document_text: str,
        page_texts: list[str],
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        page_lookup = self._build_page_lookup(page_texts)
        split_texts = self._recursive_split(document_text.strip(), self.separators)

        for index, chunk_text in enumerate(self._merge_splits(split_texts)):
            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    page_reference=self._infer_page_reference(chunk_text, page_lookup),
                    chunk_text=chunk_text,
                    chunk_index=index,
                )
            )

        return chunks

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text] if text else []

        separator = separators[0]
        remaining = separators[1:]
        if separator:
            pieces = text.split(separator)
            if len(pieces) == 1:
                return self._recursive_split(text, remaining)
            splits: list[str] = []
            for piece in pieces:
                candidate = piece.strip()
                if not candidate:
                    continue
                if len(candidate) > self.chunk_size and remaining:
                    splits.extend(self._recursive_split(candidate, remaining))
                else:
                    splits.append(candidate)
            return splits

        return [text[index : index + self.chunk_size] for index in range(0, len(text), self.chunk_size)]

    def _merge_splits(self, splits: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""

        for split in splits:
            candidate = f"{current} {split}".strip() if current else split
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current)
                current = self._tail(current) + " " + split
                current = current.strip()

            while len(current) > self.chunk_size:
                chunks.append(current[: self.chunk_size].strip())
                current = (self._tail(current[: self.chunk_size]) + current[self.chunk_size :]).strip()

        if current:
            chunks.append(current)

        return chunks

    def _tail(self, text: str) -> str:
        return text[-self.overlap :] if len(text) > self.overlap else text

    @staticmethod
    def _build_page_lookup(page_texts: list[str]) -> list[tuple[int, str]]:
        return [(index + 1, page_text.strip()) for index, page_text in enumerate(page_texts) if page_text.strip()]

    @staticmethod
    def _infer_page_reference(chunk_text: str, page_lookup: list[tuple[int, str]]) -> str:
        if not page_lookup:
            return "unknown"

        sample = chunk_text[:120].strip()
        for page_number, page_text in page_lookup:
            if sample and sample in page_text:
                return f"page {page_number}"
        return f"page {page_lookup[0][0]}"

