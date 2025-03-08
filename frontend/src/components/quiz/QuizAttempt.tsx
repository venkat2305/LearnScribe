import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuiz } from "@/hooks/useQuiz";
import QuizQuestion from "./QuizQuestion";
import { QuizResponse } from "@/types/quiz.types";
import { Progress } from "@/components/ui/progress";

export default function QuizAttempt() {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();
  const { getQuizById, currentQuiz, quizResult, isLoading, attemptQuiz, setAnswer } = useQuiz();
  const [responses, setResponses] = useState<QuizResponse[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (quizId) {
      getQuizById(quizId);
    }
  }, [quizId]);

  useEffect(() => {
    // Initialize responses from currentQuiz when it's loaded
    if (currentQuiz) {
      const initialResponses = currentQuiz.questions
        .filter(q => q.selected_choice_id)
        .map(q => ({
          question_id: q.question_id, // ensure using snake_case
          selected_choice_id: q.selected_choice_id!
        }));
      setResponses(initialResponses);
    }
  }, [currentQuiz]);

  const handleAnswerSelect = (questionId: string, choiceId: string) => {
    setAnswer(questionId, choiceId);
    
    // Update responses state
    const existingResponseIndex = responses.findIndex(r => r.question_id === questionId);
    if (existingResponseIndex !== -1) {
      const updatedResponses = [...responses];
      updatedResponses[existingResponseIndex] = { question_id: questionId, selected_choice_id: choiceId };
      setResponses(updatedResponses);
    } else {
      setResponses([...responses, { question_id: questionId, selected_choice_id: choiceId }]);
    }
  };

  const handleSubmit = async () => {
    if (!currentQuiz) return;
    
    if (responses.length < currentQuiz.questions.length) {
      toast.warning("Incomplete Quiz", {
        description: `You've answered ${responses.length} out of ${currentQuiz.questions.length} questions. Make sure to answer all questions before submitting.`
      });
      return;
    }

    setSubmitting(true);
    const result = await attemptQuiz({
      quiz_id: currentQuiz.quiz_id,
      responses: responses
    });

    setSubmitting(false);
    if (result && result.attempt_id) {
      navigate(`/quiz/result/${result.attempt_id}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-80">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading quiz...</span>
      </div>
    );
  }

  if (!currentQuiz) {
    return (
      <div className="flex flex-col items-center justify-center h-80 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Quiz not found</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          The quiz you're looking for doesn't exist or you may not have access to it.
        </p>
        <Button onClick={() => navigate("/quiz/myquizzes")}>Back to My Quizzes</Button>
      </div>
    );
  }

  const completionPercentage = Math.round((responses.length / currentQuiz.questions.length) * 100);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">{currentQuiz.quiz_title}</h1> {/* changed from quizTitle */}
        <div className="flex items-center justify-between mt-4 text-sm">
          <span className="text-muted-foreground">Difficulty: <span className="text-foreground">{currentQuiz.difficulty}</span></span>
          <span className="text-muted-foreground">Category: <span className="text-foreground">{currentQuiz.category}</span></span>
          <span className="text-muted-foreground">Questions: <span className="text-foreground">{currentQuiz.questions.length}</span></span>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm">Progress</span>
          <span className="text-sm font-medium">{completionPercentage}%</span>
        </div>
        <Progress value={completionPercentage} className="h-2" />
      </div>

      {currentQuiz.questions.map((question, index) => (
        <QuizQuestion
          key={question.question_id}
          question={question}
          index={index}
          onAnswerSelect={handleAnswerSelect}
        />
      ))}

      <div className="flex justify-end mt-8 mb-12">
        <Button 
          onClick={handleSubmit} 
          size="lg" 
          disabled={submitting || responses.length === 0}
        >
          {submitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            "Submit Quiz"
          )}
        </Button>
      </div>
    </div>
  );
}