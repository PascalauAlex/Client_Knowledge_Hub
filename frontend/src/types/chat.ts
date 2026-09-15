export interface Source {
  id: number
  title: string
  url: string | null
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}
