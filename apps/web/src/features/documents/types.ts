export type DocumentUploadResult = {
  document_id: string;
  chunks_created: number;
  entities_found: number;
  graph_nodes_created: number;
  graph_edges_created: number;
};

export type DocumentUploadResponse = DocumentUploadResult | { documents: DocumentUploadResult[] };

export type DocumentSummary = {
  document_id: string;
  filename: string;
  content_type: string;
  file_size_bytes: number;
  upload_timestamp: string;
  status: "uploaded" | "processed" | "completed" | "failed" | string;
  page_count?: number | null;
  extraction_method?: string | null;
  is_scanned: boolean;
  processed_at?: string | null;
  failed_at?: string | null;
  error?: string | null;
  extracted_entities: number;
  chunks_created: number;
  graph_nodes_created: number;
  graph_edges_created: number;
  processing_duration_ms?: number | null;
};

export type DocumentListResponse = {
  documents: DocumentSummary[];
};

export type UploadStage =
  | "queued"
  | "uploading"
  | "extracting"
  | "ocr"
  | "chunking"
  | "entities"
  | "graph"
  | "embeddings"
  | "risk"
  | "digitalTwin"
  | "completed";

export type UploadStatus = "queued" | "uploading" | "processing" | "completed" | "failed" | "cancelled";

export type UploadHistoryItem = {
  id: string;
  documentName: string;
  documentId?: string;
  status: UploadStatus;
  timestamp: string;
};
