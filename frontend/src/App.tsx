import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "sonner";
import Login from "@/pages/Auth/Login";
import Register from "@/pages/Auth/Register";
import Dashboard from "@/pages/Dashboard/Dashboard";
import CreateQuizPage from "@/pages/Quiz/CreateQuizPage";
import MyQuizzesPage from "@/pages/Quiz/MyQuizzesPage";
import QuizAttemptPage from "@/pages/Quiz/QuizAttemptPage";
import QuizResultPage from "@/pages/Quiz/QuizResultPage";
import QuizAttemptsPage from "@/pages/Quiz/QuizAttemptsPage";
import CreateSummaryPage from "@/pages/Summary/CreateSummaryPage";
import MySummariesPage from "@/pages/Summary/MySummariesPage";
import SummaryDetailPage from "@/pages/Summary/SummaryDetailPage";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import SidebarLayout from "@/components/layout/Sidebar";

function App() {
  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes with Sidebar Layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <SidebarLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route path="dashboard" element={<Dashboard />} />

          {/* Quiz Routes */}
          <Route path="quiz">
            <Route path="create" element={<CreateQuizPage />} />
            <Route path="myquizzes" element={<MyQuizzesPage />} />
            <Route path=":quizId" element={<QuizAttemptPage />} />
            <Route path="attempts/:quizId" element={<QuizAttemptsPage />} />
            <Route path="result/:attemptId" element={<QuizResultPage />} />
          </Route>

          {/* Summary Routes */}
          <Route path="summary">
            <Route path="create" element={<CreateSummaryPage />} />
            <Route path="mysummaries" element={<MySummariesPage />} />
            <Route path=":summaryId" element={<SummaryDetailPage />} />
          </Route>

          {/* Default redirect to dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>

      {/* Toast notifications */}
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: {
            background: "hsl(var(--card))",
            color: "hsl(var(--card-foreground))",
            border: "1px solid hsl(var(--border))",
          },
          className: "text-foreground",
        }}
      />
    </Router>
  );
}

export default App;
