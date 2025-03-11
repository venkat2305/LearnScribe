export interface Summary {
    summary_id: string;
    user_id: string;
    title?: string;
    summary_text?: string;
    summary?: string;
    related_questions?: {
      question: string;
      answer: string;
    }[];
    source_type: string;
    source_url?: string;
    metadata?: {
      model: string;
      service: string;
      input_tokens: number;
      output_tokens: number;
      time_taken: number;
    };
    created_at: string;
    created_by: string;
  }
  
  export interface SummaryRequest {
    summarySource: "text" | "youtube" | "article";
    contentSource?: {
      url?: string;
    };
    textContent?: string;
    prompt?: string;
    length: "short" | "medium" | "long";
  }
  
  export interface SummaryResponse {
    message: string;
    summary_id: string;
    summary: string;
  }