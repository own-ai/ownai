import { IdName } from "./IdName";

export interface Ai extends IdName {
  input_keys: string[];
  input_labels?: { [key: string]: string };
  chain: object;
  greeting?: string;
}
