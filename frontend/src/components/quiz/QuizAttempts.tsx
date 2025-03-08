import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2, AlertTriangle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuiz } from "@/hooks/useQuiz";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDate } from "@/lib/utils";

export default function QuizAttempts() {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();
  const { getQuizAttempts, quizAttempts, currentQuiz, getQuizById, isLoading } = useQuiz();

  useEffect(() => {
    if (quizId) {
      getQuizById(quizId);
      getQuizAttempts(quizId);
    }
  }, [quizId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-80">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading attempts...</span>
      </div>
    );
  }

  if (!quizAttempts || quizAttempts.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <Button 
          variant="ghost" 
          onClick={() => navigate("/quiz/myquizzes")} 
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to My Quizzes
        </Button>
        
        <div className="flex flex-col items-center justify-center h-60 text-center">
          <AlertTriangle className="h-8 w-8 text-muted-foreground mb-2" />
          <h2 className="text-xl font-semibold">No attempts found</h2>
          <p className="text-muted-foreground mt-1 mb-4">
            You haven't attempted this quiz yet.
          </p>
          <Button onClick={() => navigate(`/quiz/${quizId}`)}>Attempt Quiz</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Button 
        variant="ghost" 
        onClick={() => navigate("/quiz/myquizzes")} 
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to My Quizzes
      </Button>
      
      <h1 className="text-2xl font-bold mb-2">
        {currentQuiz ? currentQuiz.quiz_title : "Quiz"} Attempts
      </h1>
      <p className="text-muted-foreground mb-6">
        Review your previous attempts at this quiz
      </p>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Attempted On</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Correct</TableHead>
            <TableHead>Incorrect</TableHead>
            <TableHead className="text-right">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {quizAttempts.map((attempt) => (
            <TableRow key={attempt.attempt_id}>
              <TableCell className="font-medium">
                {formatDate(attempt.attempted_at)}
              </TableCell>
              <TableCell>
                {attempt.marks_obtained} / {attempt.total_marks}
                <span className="text-muted-foreground ml-2">
                  ({Math.round((attempt.marks_obtained / attempt.total_marks) * 100)}%)
                </span>
              </TableCell>
              <TableCell>{attempt.stats.correct_count}</TableCell>
              <TableCell>{attempt.stats.wrong_count}</TableCell>
              <TableCell className="text-right">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigate(`/quiz/result/${attempt.attempt_id}`)}
                >
                  View Results
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      <div className="flex justify-end mt-8">
        <Button onClick={() => navigate(`/quiz/${quizId}`)}>
          Attempt Again
        </Button>
      </div>
    </div>
  );
}
