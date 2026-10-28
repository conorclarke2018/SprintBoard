// Client-side checks that mirror the Pydantic rules, so users see errors straight away.
// The server still enforces every rule.

type Rule = (value: string) => string | null

export function lengthBetween(label: string, min: number, max: number): Rule {
  return (value) => {
    const length = value.trim().length
    if (length < min) return `${label} must be at least ${min} characters`
    if (length > max) return `${label} must be at most ${max} characters`
    return null
  }
}

export function maxLength(label: string, max: number): Rule {
  return (value) => (value.trim().length > max ? `${label} must be at most ${max} characters` : null)
}

export const validateUsername: Rule = (value) =>
  lengthBetween('Username', 3, 30)(value) ??
  (/^[a-zA-Z0-9_]+$/.test(value.trim()) ? null : 'Use only letters, numbers and underscores')

export const validatePassword: Rule = (value) =>
  value.length < 8 ? 'Password must be at least 8 characters' : null

export const validateProjectKey: Rule = (value) =>
  /^[A-Z]{2,5}$/.test(value.trim()) ? null : 'Key must be 2 to 5 letters, for example SB'

export const required =
  (label: string): Rule =>
  (value) =>
    value.trim() ? null : `${label} is required`
