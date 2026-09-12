import type { User } from './user.ts'

export interface Client {
  id: number
  name: string
  email: string
  created_by: User
}
