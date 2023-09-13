import { Ai } from "@/types/Ai";

export type BasicAi = Pick<
  Ai,
  "id" | "name" | "input_keys" | "input_labels" | "greeting"
>;
