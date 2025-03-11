import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BookOpen, FileText, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuiz } from "@/hooks/useQuiz";
import { useSummary } from "@/hooks/useSummary";

export default function Dashboard() {
  const navigate = useNavigate();
  const { quizzes, getMyQuizzes, isLoading: quizLoading } = useQuiz();
  const { summaries, getMySummaries, isLoading: summaryLoading } = useSummary();
  
  useEffect(() => {
    getMyQuizzes();
    getMySummaries();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex justify-between items-center">
              <span>Quizzes</span>
              <Button size="sm" onClick={() => navigate("/quiz/create")}>
                <Plus className="h-4 w-4 mr-1" /> Create
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              {quizLoading ? (
                <p className="text-muted-foreground">Loading quizzes...</p>
              ) : quizzes && quizzes.length > 0 ? (
                <div>
                  <p className="text-muted-foreground mb-3">You have {quizzes.length} quizzes</p>
                  <Button variant="outline" onClick={() => navigate("/quiz/myquizzes")} className="w-full">
                    <BookOpen className="h-4 w-4 mr-2" /> View All Quizzes
                  </Button>
                </div>
              ) : (
                <div>
                  <p className="text-muted-foreground mb-3">You haven't created any quizzes yet</p>
                  <Button onClick={() => navigate("/quiz/create")} className="w-full">
                    <Plus className="h-4 w-4 mr-2" /> Create Your First Quiz
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex justify-between items-center">
              <span>Summaries</span>
              <Button size="sm" onClick={() => navigate("/summary/create")}>
                <Plus className="h-4 w-4 mr-1" /> Create
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              {summaryLoading ? (
                <p className="text-muted-foreground">Loading summaries...</p>
              ) : summaries && summaries.length > 0 ? (
                <div>
                  <p className="text-muted-foreground mb-3">You have {summaries.length} summaries</p>
                  <Button variant="outline" onClick={() => navigate("/summary/mysummaries")} className="w-full">
                    <FileText className="h-4 w-4 mr-2" /> View All Summaries
                  </Button>
                </div>
              ) : (
                <div>
                  <p className="text-muted-foreground mb-3">You haven't created any summaries yet</p>
                  <Button onClick={() => navigate("/summary/create")} className="w-full">
                    <Plus className="h-4 w-4 mr-2" /> Create Your First Summary
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}