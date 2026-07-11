export type Citation = {
  document_id: string;
  document?: string | null;
  chunk_id?: string | null;
  page_reference?: string | null;
  page_number?: number | null;
  quote?: string | null;
  evidence?: string | null;
  confidence: number;
};

export type ChatApiResponse = {
  answer: string;
  confidence: number;
  citations: Citation[];
  related_assets: string[];
  follow_up_questions: string[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  confidence?: number;
  citations?: Citation[];
  relatedAssets?: string[];
  followUpQuestions?: string[];
  demoMode?: boolean;
  status?: "complete" | "streaming" | "error";
};

export type Conversation = {
  id: string;
  title: string;
  updatedAt: string;
  messages: ChatMessage[];
};

export type GraphContextItem = {
  label: string;
  value: string;
  tone: "neutral" | "good" | "warning" | "danger";
};
