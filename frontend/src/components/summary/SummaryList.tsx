import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Eye, 
  Loader2, 
  Trash2, 
  AlertTriangle,
  FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSummary } from "@/hooks/useSummary";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import dayjs from "dayjs";

export default function SummaryList() {
  const navigate = useNavigate();
  const { summaries, isLoading, error, getMySummaries, removeSummary } = useSummary();
  const [summaryToDelete, setSummaryToDelete] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  useEffect(() => {
    getMySummaries();
  }, []);
  
  const handleDeleteSummary = async () => {
    if (summaryToDelete) {
      await removeSummary(summaryToDelete);
      setDeleteDialogOpen(false);
      setSummaryToDelete(null);
    }
  };

  const getSourceTypeLabel = (sourceType: string) => {
    switch (sourceType.toLowerCase()) {
      case "text":
        return "Text";
      case "youtube":
        return "YouTube";
      case "article":
        return "Article";
      default:
        return sourceType;
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return dayjs(dateString).format("MMM D, YYYY");
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading summaries...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
        <h2 className="text-xl font-semibold">Error loading summaries</h2>
        <p className="text-muted-foreground mt-1 mb-4">{error}</p>
        <Button onClick={() => getMySummaries()}>Try Again</Button>
      </div>
    );
  }

  if (!summaries || summaries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <FileText className="h-8 w-8 text-muted-foreground mb-2" />
        <h2 className="text-xl font-semibold">No summaries found</h2>
        <p className="text-muted-foreground mt-1 mb-4">
          You haven't created any summaries yet.
        </p>
        <Button onClick={() => navigate("/summary/create")}>Create Your First Summary</Button>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border shadow-sm max-w-4xl mx-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="font-medium text-sm">Title</TableHead>
              <TableHead className="font-medium text-sm w-28">Source</TableHead>
              <TableHead className="font-medium text-sm w-32">Created</TableHead>
              <TableHead className="text-right w-20">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {summaries.map((summary) => (
              <TableRow key={summary.summary_id} className="hover:bg-muted/30">
                <TableCell className="py-2">
                  <button 
                    onClick={() => navigate(`/summary/${summary.summary_id}`)}
                    className="text-left font-medium hover:underline text-sm"
                  >
                    {summary.title || `Summary ${summary.summary_id.slice(-5)}`}
                  </button>
                </TableCell>
                <TableCell className="py-2">
                  <Badge variant="outline" className="text-xs px-2 py-0">
                    {getSourceTypeLabel(summary.source_type)}
                  </Badge>
                </TableCell>
                <TableCell className="py-2 text-sm text-muted-foreground">{formatDate(summary.created_at)}</TableCell>
                <TableCell className="text-right py-2">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/summary/${summary.summary_id}`)}
                      className="h-7 w-7 p-0"
                    >
                      <Eye className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSummaryToDelete(summary.summary_id);
                        setDeleteDialogOpen(true);
                      }}
                      className="h-7 w-7 p-0 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Summary</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this summary? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleDeleteSummary}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}