// Checks the experiment lists against the app's own accent logic, without
// touching the app. Run from the repo root:
//   npx vitest run corpus/experiments/2026-10-16-autostudy/tests
import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { stripAccents, buildAccentMap } from '../../../../src/engine/accents'

const dir = resolve(__dirname, '..', 'output')
const read = (f: string) => readFileSync(resolve(dir, f), 'utf-8').trim().split('\n').map(w => w.trim())
const answers = read('words-answer.txt')
const valid = read('words-valid.txt')
const validSet = new Set(valid.map(stripAccents))
const accentMap = buildAccentMap(valid)

describe('experiment word lists vs app logic', () => {
  it('every word has 5 letters and only Portuguese characters', () => {
    for (const w of [...answers, ...valid]) {
      expect(w, w).toMatch(/^[a-záéíóúâêôãõàüç]{5}$/)
      expect(stripAccents(w)).toMatch(/^[a-z]{5}$/)
    }
  })
  it('every answer is guessable (its unaccented key is valid)', () => {
    const missing = answers.filter(w => !validSet.has(stripAccents(w)))
    expect(missing).toEqual([])
  })
  it('valid list has exactly one spelling per unaccented key (no display ambiguity)', () => {
    expect(accentMap.size).toBe(valid.length)
  })
  it('typing an answer displays the answer itself for almost all answers', () => {
    const shown = answers.filter(w => accentMap.get(stripAccents(w)) !== w)
    // homographs differing only by accent (louca/louça) are the only exceptions
    expect(shown.length).toBeLessThan(answers.length * 0.02)
  })
  it('no duplicates', () => {
    expect(new Set(answers).size).toBe(answers.length)
    expect(new Set(valid).size).toBe(valid.length)
  })
})
