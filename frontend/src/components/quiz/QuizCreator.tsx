import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";

// UI Components
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

// Custom hooks
import { useQuiz } from "@/hooks/useQuiz";

// Constants
const QUIZ_SOURCES = {
  MANUAL: "manual",
  YOUTUBE: "youtube",
  ARTICLE: "article",
  MISTAKES: "mistakes",
};

const DIFFICULTY_LEVELS = {
  EASY: "easy",
  MEDIUM: "medium",
  HARD: "hard",
};

const QUESTION_COUNT_OPTIONS = [3, 5, 7, 10, 15, 20, 25, 30];

// Zod schema
const formSchema = z.object({
  quizSource: z.enum([
    QUIZ_SOURCES.MANUAL,
    QUIZ_SOURCES.YOUTUBE,
    QUIZ_SOURCES.ARTICLE,
    QUIZ_SOURCES.MISTAKES,
  ]),
  quizTopic: z.string().optional(),
  difficulty: z.enum([
    DIFFICULTY_LEVELS.EASY,
    DIFFICULTY_LEVELS.MEDIUM,
    DIFFICULTY_LEVELS.HARD,
  ]),
  contentSource: z
    .object({
      url: z.string().url().optional(),
    })
    .optional(),
  prompt: z
    .string()
    .min(10, "Prompt must be at least 10 characters")
    .optional(),
  numberOfQuestions: z.number().int().min(3).max(30).default(5),
});

type FormValues = z.infer<typeof formSchema>;

// Helper function to convert camelCase to snake_case
const camelToSnakeCase = (obj: Record<string, any>): Record<string, any> => {
  const result: Record<string, any> = {};

  Object.keys(obj).forEach((key) => {
    // Convert key from camelCase to snake_case
    const snakeKey = key.replace(/([A-Z])/g, "_$1").toLowerCase();

    // Handle nested objects
    if (
      obj[key] !== null &&
      typeof obj[key] === "object" &&
      !Array.isArray(obj[key])
    ) {
      result[snakeKey] = camelToSnakeCase(obj[key]);
    } else {
      result[snakeKey] = obj[key];
    }
  });

  return result;
};

export default function QuizCreator() {
  const navigate = useNavigate();
  const { createNewQuiz, isLoading } = useQuiz();
  const [sourceType, setSourceType] = useState(QUIZ_SOURCES.MANUAL);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      quizSource: QUIZ_SOURCES.MANUAL,
      difficulty: DIFFICULTY_LEVELS.MEDIUM,
      numberOfQuestions: 5,
    },
  });

  const handleSourceChange = (
    value: (typeof QUIZ_SOURCES)[keyof typeof QUIZ_SOURCES]
  ) => {
    setSourceType(value);
    form.setValue("quizSource", value);

    // Reset content source when changing source type
    if (value !== QUIZ_SOURCES.MISTAKES) {
      form.setValue("contentSource", { url: "" });
    }
  };

  const onSubmit = async (values: FormValues) => {
    const transformedValues = camelToSnakeCase(values);

    // Remove contentSource if using manual or mistakes quiz source and it's empty
    if (
      (values.quizSource === QUIZ_SOURCES.MANUAL || 
       values.quizSource === QUIZ_SOURCES.MISTAKES) &&
      transformedValues.content_source
    ) {
      delete transformedValues.content_source;
    }

    const quizId = await createNewQuiz(values, transformedValues);
    if (quizId) {
      navigate(`/quiz/${quizId}`);
    }
  };

  // Form section components
  const renderQuizSourceField = () => (
    <FormField
      control={form.control}
      name="quizSource"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Quiz Source</FormLabel>
          <FormControl>
            <RadioGroup
              onValueChange={handleSourceChange}
              defaultValue={field.value}
              className="flex flex-col space-y-1"
            >
              <SourceRadioOption
                value={QUIZ_SOURCES.MANUAL}
                label="Manual (Create from prompt)"
              />
              <SourceRadioOption
                value={QUIZ_SOURCES.YOUTUBE}
                label="YouTube Video"
              />
              <SourceRadioOption
                value={QUIZ_SOURCES.ARTICLE}
                label="Web Article"
              />
              <SourceRadioOption
                value={QUIZ_SOURCES.MISTAKES}
                label="Common Mistakes"
              />
            </RadioGroup>
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const SourceRadioOption = ({
    value,
    label,
  }: {
    value: string;
    label: string;
  }) => (
    <FormItem className="flex items-center space-x-3 space-y-0">
      <FormControl>
        <RadioGroupItem value={value} />
      </FormControl>
      <FormLabel className="font-normal">{label}</FormLabel>
    </FormItem>
  );

  const renderContentSourceField = () => {
    if (
      sourceType !== QUIZ_SOURCES.YOUTUBE &&
      sourceType !== QUIZ_SOURCES.ARTICLE
    ) {
      return null;
    }

    const isYoutube = sourceType === QUIZ_SOURCES.YOUTUBE;

    return (
      <FormField
        control={form.control}
        name="contentSource.url"
        render={({ field }) => (
          <FormItem>
            <FormLabel>{isYoutube ? "YouTube URL" : "Article URL"}</FormLabel>
            <FormControl>
              <Input
                placeholder={
                  isYoutube
                    ? "https://youtube.com/watch?v=..."
                    : "https://example.com/article..."
                }
                {...field}
              />
            </FormControl>
            <FormDescription>
              Enter the full URL of the{" "}
              {isYoutube ? "YouTube video" : "article"} you want to create a
              quiz from
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  };

  const renderQuizTopicField = () => {
    if (sourceType !== QUIZ_SOURCES.MANUAL) {
      return null;
    }

    return (
      <FormField
        control={form.control}
        name="quizTopic"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Quiz Topic (Optional)</FormLabel>
            <FormControl>
              <Input
                placeholder="e.g., JavaScript Basics, World History, etc."
                {...field}
              />
            </FormControl>
            <FormDescription>Specify a topic for your quiz</FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    );
  };

  const renderDifficultyField = () => (
    <FormField
      control={form.control}
      name="difficulty"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Difficulty Level</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select difficulty" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value={DIFFICULTY_LEVELS.EASY}>Easy</SelectItem>
              <SelectItem value={DIFFICULTY_LEVELS.MEDIUM}>Medium</SelectItem>
              <SelectItem value={DIFFICULTY_LEVELS.HARD}>Hard</SelectItem>
            </SelectContent>
          </Select>
          <FormDescription>
            Choose the difficulty level for your quiz
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const renderNumberOfQuestionsField = () => (
    <FormField
      control={form.control}
      name="numberOfQuestions"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Number of Questions</FormLabel>
          <Select
            onValueChange={(value) => field.onChange(parseInt(value, 10))}
            defaultValue={field.value.toString()}
          >
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select number of questions" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {QUESTION_COUNT_OPTIONS.map((count) => (
                <SelectItem key={count} value={count.toString()}>
                  {count}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormDescription>
            Choose how many questions to include in your quiz
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const renderPromptField = () => (
    <FormField
      control={form.control}
      name="prompt"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Prompt</FormLabel>
          <FormControl>
            <Textarea
              placeholder="Describe the quiz content you want to generate..."
              className="min-h-32"
              {...field}
            />
          </FormControl>
          <FormDescription>
            Provide details about the quiz you want to create
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const renderSubmitButton = () => (
    <div className="flex justify-end">
      <Button type="submit" disabled={isLoading} className="w-full md:w-auto">
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating Quiz...
          </>
        ) : (
          "Create Quiz"
        )}
      </Button>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create New Quiz</CardTitle>
          <CardDescription>
            Generate a quiz using AI based on your preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {renderQuizSourceField()}
              {renderContentSourceField()}
              {renderQuizTopicField()}
              {renderDifficultyField()}
              {renderNumberOfQuestionsField()}
              {renderPromptField()}
              {renderSubmitButton()}
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
