export function stripAccents(word: string): string {
  return word.normalize('NFD').replace(/[\u0300-\u036f\u0327]/g, '')
}

export function buildAccentMap(words: string[]): Map<string, string> {
  const map = new Map<string, string>()
  for (const word of words) {
    map.set(stripAccents(word), word)
  }
  return map
}
