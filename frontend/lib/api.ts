import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL: API_BASE });

export interface AgentStep {
  agent: string;
  action: string;
  summary: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  agent_trace: AgentStep[];
  sources: string[];
}

export async function sendChatMessage(message: string, conversationId?: string): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", {
    message,
    conversation_id: conversationId ?? null,
  });
  return data;
}

export interface ForecastPoint {
  period: string;
  predicted: number;
  lower: number;
  upper: number;
}

export async function getForecast(target: string, horizon = 30) {
  const { data } = await api.post<{ forecast: ForecastPoint[]; metrics: Record<string, number> }>(
    "/forecast",
    { target, horizon }
  );
  return data;
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getExecutiveSummary(period = "last_30_days") {
  const { data } = await api.post("/reports/executive-summary", { period, focus_areas: [] });
  return data;
}
