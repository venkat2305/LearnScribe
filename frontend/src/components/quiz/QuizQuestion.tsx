import { useState } from "react";
import { Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { QuizQuestion as QuizQuestionType } from "@/types/quiz.types";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface QuizQuestionProps {
  question: QuizQuestionType;
  index: number;
  isResult?: boolean;
  onAnswerSelect?: (question_id: string, choice_id: string) => void;
}

export default function QuizQuestion({
  question,
  index,
  isResult = false,
  onAnswerSelect,
}: QuizQuestionProps) {
  const [selectedChoiceId, setSelectedChoiceId] = useState<string | undefined>(
    question.selected_choice_id
  );

  const handleChoiceSelect = (choice_id: string) => {
    if (isResult) return;
    
    setSelectedChoiceId(choice_id);
    if (onAnswerSelect) {
      onAnswerSelect(question.question_id, choice_id);
    }
  };

  const getChoiceClassName = (choice_id: string) => {
    if (!isResult) {
      return cn(
        "p-4 border rounded-md mb-2 cursor-pointer transition-colors",
        selectedChoiceId === choice_id
          ? "border-primary bg-primary/10"
          : "border-border hover:border-primary/50 hover:bg-primary/5"
      );
    }

    // For result view
    const isSelected = question.selected_choice_id === choice_id;
    const isCorrect = question.correct_choice_id === choice_id;

    return cn(
      "p-4 border rounded-md mb-2",
      isSelected && isCorrect && "border-green-500 bg-green-500/10",
      isSelected && !isCorrect && "border-red-500 bg-red-500/10",
      !isSelected && isCorrect && "border-green-500 bg-green-500/10",
      !isSelected && !isCorrect && "border-border"
    );
  };

  return (
    <div className="mb-8 p-6 bg-card rounded-lg border border-border">
      <div className="mb-4">
        <h3 className="font-medium text-lg flex gap-2 items-center">
          <span className="bg-primary/20 text-primary px-2 py-1 rounded-md">
            {index + 1}
          </span>
          {question.question_text}
        </h3>
      </div>

      <div className="space-y-2">
        {question.choices.map((choice) => (
          <div
            key={choice.choice_id}
            className={getChoiceClassName(choice.choice_id)}
            onClick={() => handleChoiceSelect(choice.choice_id)}
          >
            <div className="flex justify-between items-center">
              <div>{choice.choice_text}</div>
              {isResult && choice.choice_explanation && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button className="text-muted-foreground hover:text-foreground">
                        <Info size={16} />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="left" className="max-w-xs">
                      <p>{choice.choice_explanation}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
            </div>
          </div>
        ))}
      </div>

      {isResult && question.answer_explanation && (
        <div className="mt-4 p-3 bg-secondary/30 rounded-md">
          <h4 className="font-medium mb-1">Explanation:</h4>
          <p className="text-sm">{question.answer_explanation}</p>
        </div>
      )}
    </div>
  );
}