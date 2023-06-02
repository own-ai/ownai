import { IdName } from "./IdName";

export interface Knowledge extends IdName {
  embeddings: string;
  chunk_size: number;
}
