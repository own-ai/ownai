export function slugify(text: string): string {
  return text
    .normalize("NFKD") // normalize() using NFKD form converts accented characters
    .toLowerCase() // Convert the string to lowercase letters
    .trim() // Remove whitespace from both sides of the string
    .replace(/\s+/g, "-") // Replace spaces with -
    .replace(/[^\w\-]+/g, "") // Remove all non-word chars
    .replace(/\_/g, "-") // Replace _ with -
    .replace(/\-\-+/g, "-") // Replace multiple - with single -
    .replace(/\-$/g, ""); // Remove trailing -
}
