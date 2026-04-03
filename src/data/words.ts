import answersRaw from './answers.txt?raw'
import validRaw from './valid.txt?raw'
import { stripAccents, buildAccentMap } from '../engine/accents'

const answerList: string[] = answersRaw.trim().split('\n').map(w => w.trim())
const validList: string[] = validRaw.trim().split('\n').map(w => w.trim())

const validAccentMap = buildAccentMap(validList)
const validUnaccentedSet = new Set(validList.map(stripAccents))

export function isValidWord(unaccentedInput: string): boolean {
  return validUnaccentedSet.has(unaccentedInput)
}

export function resolveAccented(unaccentedInput: string): string {
  return validAccentMap.get(unaccentedInput) ?? unaccentedInput
}

function hashToSeed(key: string): number {
  let h = 2166136261 >>> 0
  for (let i = 0; i < key.length; i++) {
    h = Math.imul(h ^ key.charCodeAt(i), 16777619) >>> 0
  }
  return h
}

function makePrng(seed: number): () => number {
  let s = seed
  return () => {
    s = (s + 0x6d2b79f5) >>> 0
    let z = Math.imul(s ^ (s >>> 15), 1 | s)
    z = (z + Math.imul(z ^ (z >>> 7), 61 | z)) ^ z
    return ((z ^ (z >>> 14)) >>> 0) / 4294967296
  }
}

export function getDailyWord(dateKey: string): string {
  const rng = makePrng(hashToSeed(dateKey + ':termo'))
  const index = Math.floor(rng() * answerList.length)
  return answerList[index]
}

export function getDateKey(date: Date = new Date()): string {
  return date.toISOString().slice(0, 10)
}

export function getDailyWords(dateKey: string, count: number, mode: string): string[] {
  const rng = makePrng(hashToSeed(dateKey + ':' + mode))
  const words: string[] = []
  while (words.length < count) {
    const index = Math.floor(rng() * answerList.length)
    const word = answerList[index]
    if (!words.includes(word)) words.push(word)
  }
  return words
}

export { answerList, validList }
