import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2, AlertTriangle, ArrowLeft, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSummary } from "@/hooks/useSummary";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import dayjs from "dayjs";

export default function SummaryDetail() {
  const { summaryId } = useParams<{ summaryId: string }>();
  const navigate = useNavigate();
  const { getSummaryById, currentSummary, isLoading } = useSummary();

  console.log("currentSummary", typeof currentSummary?.summary);

  useEffect(() => {
    if (summaryId) {
      getSummaryById(summaryId);
    }
  }, [summaryId]);

  const formatDate = (dateString: string) => {
    try {
      return dayjs(dateString).format("MMM D, YYYY");
    } catch (error) {
      return dateString;
    }
  };

  const getSourceTypeLabel = (sourceType: string) => {
    switch (sourceType?.toLowerCase()) {
      case "text":
        return "Text";
      case "youtube":
        return "YouTube";
      case "article":
        return "Web Article";
      default:
        return sourceType || "Unknown";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-80">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading summary...</span>
      </div>
    );
  }

  if (!currentSummary) {
    return (
      <div className="flex flex-col items-center justify-center h-80 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Summary not found</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          The summary you're looking for doesn't exist or you may not have access to it.
        </p>
        <Button onClick={() => navigate("/summary/mysummaries")}>Back to My Summaries</Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Button 
        variant="ghost" 
        onClick={() => navigate("/summary/mysummaries")} 
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to My Summaries
      </Button>

      <Card className="mb-8">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-2xl">
                {currentSummary.title || `Summary ${currentSummary.summary_id.slice(-5)}`}
              </CardTitle>
              <CardDescription className="mt-1">
                {formatDate(currentSummary.created_at)}
              </CardDescription>
            </div>
            <Badge variant="outline">
              {getSourceTypeLabel(currentSummary.source_type)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {currentSummary.source_url && (
            <div className="mb-4 flex items-center text-sm text-muted-foreground">
              <span className="font-medium mr-1">Source:</span>
              <a 
                href={currentSummary.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary hover:underline flex items-center"
              >
                {currentSummary.source_url.length > 40 
                  ? `${currentSummary.source_url.substring(0, 40)}...` 
                  : currentSummary.source_url
                }
                <ExternalLink className="h-3 w-3 ml-1" />
              </a>
            </div>
          )}

          <div className="prose prose-sm dark:prose-invert max-w-none">
            {(currentSummary.summary_text || currentSummary.summary || "No content available").split('\n').map((paragraph: string, index: number) => (
              <p key={index} className="mb-4 last:mb-0">{paragraph}</p>
            ))}
          </div>
        </CardContent>
      </Card>

      {currentSummary.related_questions && currentSummary.related_questions.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Related Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              {currentSummary.related_questions.map((qa, index) => (
                <AccordionItem key={index} value={`item-${index}`}>
                  <AccordionTrigger className="text-left">
                    {qa.question}
                  </AccordionTrigger>
                  <AccordionContent>
                    <p className="text-muted-foreground">{qa.answer}</p>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>
      )}
    </div>
  );
}