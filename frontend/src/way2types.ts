export interface Way2Page {
  title: string;
  url: string;
  description: string;
  highlights: string[];
}
export interface Way2Site {
  id: string;
  name: string;
  domain: string;
  role: string;
  tagline: string;
  description: string;
  pages: Way2Page[];
}
export interface Way2SiblingService {
  name: string;
  domain: string;
}
export interface Way2Content {
  sites: Way2Site[];
  siblingServices: Way2SiblingService[];
}
