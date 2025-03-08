import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Loader2, 
  Trash2, 
  AlertTriangle,
  BookOpen,
} from "lucide-react";
import dayjs from "dayjs";
import { Button } from "@/components/ui/button";
import { useQuiz } from "@/hooks/useQuiz";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

export default function QuizList() {
  const navigate = useNavigate();
  const { quizzes, isLoading, error, getMyQuizzes, removeQuiz } = useQuiz();
  const [quizToDelete, setQuizToDelete] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  useEffect(() => {
    getMyQuizzes();
  }, []);
  
  const handleDeleteQuiz = async () => {
    if (quizToDelete) {
      await removeQuiz(quizToDelete);
      setDeleteDialogOpen(false);
      setQuizToDelete(null);
    }
  };
  
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case "easy":
        return "bg-green-500/20 text-green-500";
      case "medium":
        return "bg-yellow-500/20 text-yellow-500";
      case "hard":
        return "bg-orange-500/20 text-orange-500";
      case "very_hard":
      case "very hard":
        return "bg-red-500/20 text-red-500";
      default:
        return "bg-primary/20 text-primary";
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return dayjs(dateString).format('MMMM D, YYYY');
    } catch (error) {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading quizzes...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Error loading quizzes</h2>
        <p className="text-muted-foreground mt-1 mb-4">{error}</p>
        <Button onClick={() => getMyQuizzes()}>Try Again</Button>
      </div>
    );
  }

  if (!quizzes || quizzes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <BookOpen className="h-8 w-8 text-muted-foreground mb-2" />
        <h2 className="text-xl font-semibold">No quizzes found</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          You haven't created any quizzes yet.
        </p>
        <Button onClick={() => navigate("/quiz/create")}>Create Your First Quiz</Button>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quizzes.map((quiz) => (
          <Card key={quiz.quiz_id} className="flex flex-col">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="line-clamp-2">{quiz.quiz_title}</CardTitle>
                  <CardDescription className="mt-1">
                    {formatDate(quiz.created_at)}
                  </CardDescription>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8 text-destructive"
                  onClick={() => {
                    setQuizToDelete(quiz.quiz_id);
                    setDeleteDialogOpen(true);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pb-2">
              <div className="flex flex-wrap gap-2 mb-2">
                <Badge variant="outline" className={getDifficultyColor(quiz.difficulty)}>
                  {quiz.difficulty}
                </Badge>
                {quiz.category && (
                  <Badge variant="outline">
                    {quiz.category}
                  </Badge>
                )}
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{quiz.questions_count || 0} questions</span>
                <span>{quiz.attempt_count || 0} attempts</span>
              </div>
            </CardContent>
            <CardFooter className="pt-2 mt-auto grid grid-cols-2 gap-2">
              <Button 
                variant="outline"
                onClick={() => navigate(`/quiz/attempts/${quiz.quiz_id}`)}
                className="w-full"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                View Attempts
              </Button>
              <Button 
                className="w-full"
                onClick={() => navigate(`/quiz/${quiz.quiz_id}`)}
              >
                Attempt Quiz
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Quiz</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this quiz? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleDeleteQuiz}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}