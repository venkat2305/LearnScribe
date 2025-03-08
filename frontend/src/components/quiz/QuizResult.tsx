import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import QuizQuestion from "./QuizQuestion";
import { useQuiz } from "@/hooks/useQuiz";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { formatDate } from "@/lib/utils";

export default function QuizResult() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();
  const { getQuizAttempt, quizResult, isLoading } = useQuiz();

  console.log("in quiz result");
  useEffect(() => {
    if (attemptId) {
      getQuizAttempt(attemptId);
    }
  }, [attemptId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-80">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading results...</span>
      </div>
    );
  }

  if (!quizResult) {
    return (
      <div className="flex flex-col items-center justify-center h-80 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Results not available</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          We couldn't find the results for this quiz attempt.
        </p>
        <Button onClick={() => navigate("/quiz/myquizzes")}>Back to My Quizzes</Button>
      </div>
    );
  }

  if (!quizResult?.stats) {
    return (
      <div className="flex flex-col items-center justify-center h-80 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Results not available</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          Quiz stats are missing or incomplete.
        </p>
        <Button onClick={() => navigate("/quiz/myquizzes")}>Back to My Quizzes</Button>
      </div>
    );
  }

  const scorePercentage = Math.round(
    (quizResult.stats.marks_obtained / quizResult.stats.total_marks) * 100
  );
  
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Quiz Results</h1>
        <p className="text-muted-foreground">
          Attempt on {formatDate(quizResult.attempted_at)}
        </p>
      </div>
      
      <Card className="mb-8 bg-card">
        <CardHeader className="pb-3">
          <CardTitle>Your Score</CardTitle>
          <CardDescription>Here's how you performed on this quiz</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row justify-between mb-6">
            <div className="flex items-center mb-4 md:mb-0">
              <div className="w-24 h-24 rounded-full bg-card flex items-center justify-center border-4 border-primary">
                <span className="text-2xl font-bold">
                  {scorePercentage}%
                </span>
              </div>
              <div className="ml-4">
                <div className="text-sm text-muted-foreground">Score</div>
                <div className="text-xl font-semibold">
                  {quizResult.stats.marks_obtained} / {quizResult.stats.total_marks}
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                <div>
                  <div className="text-sm text-muted-foreground">Correct</div>
                  <div className="font-medium">{quizResult.stats.correct_count}</div>
                </div>
              </div>
              <div className="flex items-center">
                <XCircle className="h-5 w-5 text-red-500 mr-2" />
                <div>
                  <div className="text-sm text-muted-foreground">Incorrect</div>
                  <div className="font-medium">{quizResult.stats.wrong_count}</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <h2 className="text-xl font-semibold mb-4">Review Your Answers</h2>
      
      {quizResult.questions.map((question, index) => (
        <QuizQuestion
          key={question.question_id}
          question={{
            question_id: question.question_id,
            question_text: question.question_text,
            choices: question.choices,
            selected_choice_id: question.selected_choice_id,
            correct_choice_id: question.correct_choice_id,
            answer_explanation: question.answer_explanation,
          }}
          index={index}
          isResult={true}
        />
      ))}
      
      <div className="flex justify-between mt-8 mb-12">
        <Button 
          variant="outline"
          onClick={() => navigate(`/quiz/attempts/${quizResult.quiz_id}`)}
        >
          View All Attempts
        </Button>
        
        <Button 
          onClick={() => navigate(`/quiz/${quizResult.quiz_id}`)}
        >
          Try Again
        </Button>
      </div>
    </div>
  );
}