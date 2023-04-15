import type { Author } from './Author';

export interface Message {
  id: number;
  author: Author;
  date: Date;
  text: string;
}
