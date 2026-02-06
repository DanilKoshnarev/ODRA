/**
 * API client for ODRA backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface AuditRunRequest {
  goal: string;
  scope?: string;
  priority: number;
}

interface AuditJobResponse {
  job_id: string;
  status: string;
  created_at: string;
}

interface AuditStatusResponse {
  job_id: string;
  status: string;
  progress_percent: number;
  total_documents: number;
  processed_documents: number;
  metrics: Record<string, number>;
  current_iteration: number;
}

interface AuditReport {
  job_id: string;
  goal: string;
  status: string;
  total_evidence: number;
  precision: number;
  recall: number;
  evidence: Array<{
    doc_id: string;
    snippet: string;
    relevance_score: number;
    metadata: Record<string, any>;
  }>;
  summary: string;
  recommendations: string[];
  generated_at: string;
}

class ODRAClient {
  private apiKey: string;

  constructor(apiKey: string = "dev-key-change-in-production") {
    this.apiKey = apiKey;
  }

  private getHeaders() {
    return {
      "X-API-Key": this.apiKey,
      "Content-Type": "application/json",
    };
  }

  async runAudit(request: AuditRunRequest): Promise<AuditJobResponse> {
    const response = await fetch(`${API_BASE_URL}/audit/run`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  async getAuditStatus(jobId: string): Promise<AuditStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/audit/status/${jobId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  async getAuditReport(jobId: string): Promise<AuditReport> {
    const response = await fetch(`${API_BASE_URL}/audit/report/${jobId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  async submitFeedback(
    jobId: string,
    docId: string,
    feedback: string,
    comment?: string
  ): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/audit/feedback/${jobId}`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ doc_id: docId, feedback, comment }),
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  async uploadDocuments(files: File[]): Promise<any> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    const response = await fetch(`${API_BASE_URL}/ingest/batch`, {
      method: "POST",
      headers: { "X-API-Key": this.apiKey },
      body: formData,
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  async getHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }
}

export const apiClient = new ODRAClient();
export type { AuditRunRequest, AuditJobResponse, AuditStatusResponse, AuditReport };
