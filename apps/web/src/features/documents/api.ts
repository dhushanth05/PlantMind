import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { DocumentListResponse, DocumentSummary, DocumentUploadResponse, DocumentUploadResult } from "./types";

const documentsClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180_000,
});

export async function uploadPdfDocuments(
  files: File[],
  signal: AbortSignal,
  onUploadProgress: (progress: number) => void,
) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await documentsClient.post<DocumentUploadResponse>("/documents/upload", formData, {
    signal,
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (event) => {
      if (!event.total) {
        return;
      }

      onUploadProgress(Math.min(100, Math.round((event.loaded / event.total) * 100)));
    },
  });

  return normalizeUploadResponse(response.data);
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const response = await documentsClient.get<DocumentListResponse>("/documents");
  return response.data.documents;
}

export function getUploadErrorMessage(error: unknown) {
  if (axios.isCancel(error)) {
    return "Upload cancelled.";
  }

  if (axios.isAxiosError(error)) {
    const detail = error.response?.data;

    if (typeof detail === "string") {
      return detail;
    }

    if (detail && typeof detail === "object" && "detail" in detail) {
      const message = detail.detail;
      return typeof message === "string" ? message : "The document upload failed.";
    }

    if (error.code === "ECONNABORTED") {
      return "The upload timed out while the backend was processing the document.";
    }
  }

  return error instanceof Error ? error.message : "The document upload failed.";
}

export function isCancelledUpload(error: unknown) {
  return axios.isCancel(error);
}

function normalizeUploadResponse(response: DocumentUploadResponse): DocumentUploadResult[] {
  if ("documents" in response) {
    return response.documents;
  }

  return [response];
}
