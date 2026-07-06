export type DocumentUploadResult = {
  document_id: string;
  chunks_created: number;
  entities_found: number;
  graph_nodes_created: number;
  graph_edges_created: number;
};

export type DocumentUploadResponse = DocumentUploadResult | { documents: DocumentUploadResult[] };

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
