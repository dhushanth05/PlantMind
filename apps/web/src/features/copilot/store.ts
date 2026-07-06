import { create } from "zustand";

import type { ChatMessage, Conversation } from "./types";

const now = () => new Date().toISOString();

const initialConversation: Conversation = {
  id: "session-p204",
  title: "Pump P204 reliability",
  updatedAt: now(),
  messages: [
    {
      id: "welcome",
      role: "assistant",
      content:
        "Ask PlantMind about industrial assets, incidents, procedures, and evidence. I will answer from retrieved context and show citations when available.",
      createdAt: now(),
      confidence: 0.98,
      citations: [],
      relatedAssets: ["P204", "V112", "C301"],
      followUpQuestions: [
        "Why is Pump P204 failing repeatedly?",
        "Which SOP should be followed before maintenance?",
      ],
      status: "complete",
    },
  ],
};

type CopilotState = {
  conversations: Conversation[];
  activeConversationId: string;
  isStreaming: boolean;
  setActiveConversation: (conversationId: string) => void;
  startConversation: () => string;
  appendMessage: (conversationId: string, message: ChatMessage) => void;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  clearConversation: (conversationId: string) => void;
  setStreaming: (isStreaming: boolean) => void;
};

export const useCopilotStore = create<CopilotState>((set) => ({
  conversations: [initialConversation],
  activeConversationId: initialConversation.id,
  isStreaming: false,
  setActiveConversation: (activeConversationId) => set({ activeConversationId }),
  startConversation: () => {
    const id = `session-${crypto.randomUUID()}`;
    const conversation: Conversation = {
      id,
      title: "New investigation",
      updatedAt: now(),
      messages: [],
    };
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      activeConversationId: id,
    }));
    return id;
  },
  appendMessage: (conversationId, message) =>
    set((state) => ({
      conversations: state.conversations.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              title:
                conversation.messages.length === 0 && message.role === "user"
                  ? message.content.slice(0, 58)
                  : conversation.title,
              updatedAt: now(),
              messages: [...conversation.messages, message],
            }
          : conversation,
      ),
    })),
  updateMessage: (conversationId, messageId, updates) =>
    set((state) => ({
      conversations: state.conversations.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              updatedAt: now(),
              messages: conversation.messages.map((message) =>
                message.id === messageId ? { ...message, ...updates } : message,
              ),
            }
          : conversation,
      ),
    })),
  clearConversation: (conversationId) =>
    set((state) => ({
      conversations: state.conversations.map((conversation) =>
        conversation.id === conversationId ? { ...conversation, messages: [], updatedAt: now() } : conversation,
      ),
    })),
  setStreaming: (isStreaming) => set({ isStreaming }),
}));

export function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: now(),
    status: role === "assistant" ? "streaming" : "complete",
  };
}

