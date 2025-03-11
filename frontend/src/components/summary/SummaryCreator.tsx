import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSummary } from "@/hooks/useSummary";
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

const textSchema = z.object({
  summarySource: z.literal("text"),
  textContent: z.string().min(20, "Content must be at least 20 characters"),
  length: z.enum(["short", "medium", "long"]),
});

const youtubeSchema = z.object({
  summarySource: z.literal("youtube"),
  contentSource: z.object({
    url: z.string().url("Invalid URL").nonempty("URL is required"),
  }),
  length: z.enum(["short", "medium", "long"]),
});

const articleSchema = z.object({
  summarySource: z.literal("article"),
  contentSource: z.object({
    url: z.string().url("Invalid URL").nonempty("URL is required"),
  }),
  length: z.enum(["short", "medium", "long"]),
});

const formSchema = z.discriminatedUnion("summarySource", [
  textSchema,
  youtubeSchema,
  articleSchema,
]);

type FormValues = z.infer<typeof formSchema>;

export default function SummaryCreator() {
  const navigate = useNavigate();
  const { createSummary, isLoading } = useSummary();
  const [sourceType, setSourceType] = useState<"text" | "youtube" | "article">("text");

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      summarySource: "text",
      length: "medium",
    },
  });

  const onSubmit = async (values: FormValues) => {
    console.log("values");
    try {
      const summaryId = await createSummary(values);
      if (summaryId) {
        navigate(`/summary/${summaryId}`);
      }
    } catch (error) {
      console.error('Error creating summary:', error);
    }
  };

  const handleSourceChange = (value: "text" | "youtube" | "article") => {
    setSourceType(value);
    form.setValue("summarySource", value);
    
    // Reset content source when changing source type
    form.setValue("contentSource", { url: "" });
    form.setValue("textContent", "");
  };

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create Summary</CardTitle>
          <CardDescription>
            Generate a summary using AI based on your preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="summarySource"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Summary Source</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={(value) => handleSourceChange(value as "text" | "youtube" | "article")}
                        defaultValue={field.value}
                        className="flex flex-col space-y-1"
                      >
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="text" />
                          </FormControl>
                          <FormLabel className="font-normal">
                            Text
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
                        Enter the full URL of the {sourceType === "youtube" ? "YouTube video" : "article"} you want to summarize
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {sourceType === "text" && (
                <FormField
                  control={form.control}
                  name="textContent"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Content to Summarize</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Paste or type the text you want to summarize..."
                          className="min-h-60"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>
                        Enter or paste the text content you want to summarize
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <FormField
                control={form.control}
                name="length"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Summary Length</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select summary length" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="short">Short</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="long">Long</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose how detailed you want your summary to be
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
                      Generating Summary...
                    </>
                  ) : (
                    "Generate Summary"
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