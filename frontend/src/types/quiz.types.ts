export interface Choice {
  choice_id: string;
  choice_text: string;
  choice_explanation?: string; // Only available in results
}

export interface Question {
  question_id: string;
  question_text: string;
  choices: Choice[];
  correct_choice_id?: string; // Only available in results
  answer_explanation?: string; // Only available in results
}

export interface QuizQuestion extends Question {
  selected_choice_id?: string; // For tracking user's selection
}

export interface Quiz {
  quiz_id: string;
  quiz_title: string;
  difficulty: string;
  category: string;
  quiz_source: string;
  source_id: string;
  created_by: string;
  created_at: string;
  questions: QuizQuestion[];
}

export interface QuizResponse {
  question_id: string;
  selected_choice_id: string;
}

export interface QuizAttemptRequest {
  quiz_id: string;
  responses: QuizResponse[];
}

export interface QuestionResult {
  question_id: string;
  question_text: string;
  selected_choice_id: string;
  correct_choice_id: string;
  answer_explanation: string;
  choices: Array<{
    choice_id: string;
    choice_text: string;
    choice_explanation: string;
  }>;
}

export interface QuizResult {
  quiz_id: string;
  correct_count: number;
  wrong_count: number;
  total_questions: number;
  wrong_question_ids: string[];
  marks_obtained: number;
  total_marks: number;
  questions: QuestionResult[];
}