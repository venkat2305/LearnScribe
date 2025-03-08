import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import dayjs from "dayjs";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string) {
  try {
    return dayjs(dateString).format("MMMM D, YYYY h:mm A");
  } catch (error) {
    return dateString;
  }
}