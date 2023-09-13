import { Ai } from "./Ai";

export type Aifile = Omit<Ai, "id" | "input_keys"> & { aifileversion: number };
