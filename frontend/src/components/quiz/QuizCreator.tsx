import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuiz } from "@/hooks/useQuiz";
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
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  RadioGroup,
  RadioGroupItem,
} from "@/components/ui/radio-group";

const formSchema = z.object({
  quizSource: z.enum(["manual", "youtube", "article"]),
  quizTopic: z.string().optional(),
  difficulty: z.enum(["easy", "medium", "hard", "very_hard"]),
  contentSource: z.object({
    url: z.string().url().optional(),
  }).optional(),
  prompt: z.string().min(10, "Prompt must be at least 10 characters").optional(),
  numberOfQuestions: z.number().int().min(3).max(30).default(5),
});

type FormValues = z.infer<typeof formSchema>;

// Helper function to convert camelCase to snake_case
const camelToSnakeCase = (obj: Record<string, any>): Record<string, any> => {
  const result: Record<string, any> = {};
  
  Object.keys(obj).forEach(key => {
    // Convert key from camelCase to snake_case
    const snakeKey = key.replace(/([A-Z])/g, "_$1").toLowerCase();
    
    // Handle nested objects
    if (obj[key] !== null && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
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
  const [sourceType, setSourceType] = useState<"manual" | "youtube" | "article">("manual");

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      quizSource: "manual",
      difficulty: "medium",
      numberOfQuestions: 5,
    },
  });

  const onSubmit = async (values: FormValues) => {
    // Transform form values from camelCase to snake_case
    const transformedValues = camelToSnakeCase(values);
    
    // Remove contentSource if using manual quiz source and it's empty
    if (values.quizSource === "manual" && transformedValues.content_source) {
      delete transformedValues.content_source;
    }
    
    // Pass both original values and transformed values to the hook
    // This way the hook can use the transformed values for API calls
    // but still refer to original property names if needed
    const quizId = await createNewQuiz(values, transformedValues);
    if (quizId) {
      navigate(`/quiz/${quizId}`);
    }
  };

  const handleSourceChange = (value: "manual" | "youtube" | "article") => {
    setSourceType(value);
    form.setValue("quizSource", value);
    
    // Reset content source when changing source type
    form.setValue("contentSource", { url: "" });
  };

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
              <FormField
                control={form.control}
                name="quizSource"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quiz Source</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={(value) => handleSourceChange(value as "manual" | "youtube" | "article")}
                        defaultValue={field.value}
                        className="flex flex-col space-y-1"
                      >
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="manual" />
                          </FormControl>
                          <FormLabel className="font-normal">
                            Manual (Create from prompt)
                          </FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="youtube" />
                          </FormControl>
                          <FormLabel className="font-normal">
                            YouTube Video
                          </FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="article" />
                          </FormControl>
                          <FormLabel className="font-normal">
                            Web Article
                          </FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {(sourceType === "youtube" || sourceType === "article") && (
                <FormField
                  control={form.control}
                  name="contentSource.url"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        {sourceType === "youtube" ? "YouTube URL" : "Article URL"}
                      </FormLabel>
                      <FormControl>
                        <Input 
                          placeholder={sourceType === "youtube" 
                            ? "https://youtube.com/watch?v=..." 
                            : "https://example.com/article..."
                          } 
                          {...field} 
                        />
                      </FormControl>
                      <FormDescription>
                        Enter the full URL of the {sourceType === "youtube" ? "YouTube video" : "article"} you want to create a quiz from
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {(sourceType === "manual") && (
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
                      <FormDescription>
                        Specify a topic for your quiz
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <FormField
                control={form.control}
                name="difficulty"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Difficulty Level</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select difficulty" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="easy">Easy</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="hard">Hard</SelectItem>
                        <SelectItem value="very_hard">Very Hard</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose the difficulty level for your quiz
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

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
                        <SelectItem value="3">3</SelectItem>
                        <SelectItem value="5">5</SelectItem>
                        <SelectItem value="7">7</SelectItem>
                        <SelectItem value="10">10</SelectItem>
                        <SelectItem value="15">15</SelectItem>
                        <SelectItem value="20">20</SelectItem>
                        <SelectItem value="25">25</SelectItem>
                        <SelectItem value="30">30</SelectItem>
                        </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose how many questions to include in your quiz
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

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

              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full md:w-auto"
                >
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
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}