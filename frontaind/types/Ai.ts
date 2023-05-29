import { IdName } from "./IdName";

export interface Ai extends IdName {
  input_keys: string[];
  chain: object;
}
