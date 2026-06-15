'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface UserProfile {
  nome: string
  email: string
}

interface AuthContextType {
  isAuthenticated: boolean
  currentUser: UserProfile | null
  savedProfiles: UserProfile[]
  login: (nome: string, email: string) => void
  switchProfile: (email: string) => void
  logoutCurrent: () => void
  removeProfile: (email: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null)
  const [savedProfiles, setSavedProfiles] = useState<UserProfile[]>([])

  useEffect(() => {
    const profiles = JSON.parse(localStorage.getItem('valrat_profiles') || '[]')
    const current = localStorage.getItem('valrat_current_user')
    
    setSavedProfiles(profiles)
    
    if (current) {
      const user = JSON.parse(current)
      setCurrentUser(user)
      setIsAuthenticated(true)
    }
  }, [])

  // Login inicial ou adição de nova conta
  const login = (nome: string, email: string) => {
    const newUser = { nome, email }
    
    // Atualiza a lista de perfis salvos evitando duplicatas
    const profiles = JSON.parse(localStorage.getItem('valrat_profiles') || '[]')
    const updatedProfiles = profiles.filter((p: UserProfile) => p.email !== email)
    updatedProfiles.push(newUser)
    
    localStorage.setItem('valrat_profiles', JSON.stringify(updatedProfiles))
    localStorage.setItem('valrat_current_user', JSON.stringify(newUser))
    
    setSavedProfiles(updatedProfiles)
    setCurrentUser(newUser)
    setIsAuthenticated(true)
  }

  // Alternar rapidamente entre perfis já logados
  const switchProfile = (email: string) => {
    const target = savedProfiles.find(p => p.email === email)
    if (target) {
      localStorage.setItem('valrat_current_user', JSON.stringify(target))
      setCurrentUser(target)
      setIsAuthenticated(true)
    }
  }

  // Sair apenas da conta atual (mantém o perfil salvo para troca rápida)
  const logoutCurrent = () => {
    localStorage.removeItem('valrat_current_user')
    setCurrentUser(null)
    setIsAuthenticated(false)
  }

  // Remover completamente o perfil do dispositivo
  const removeProfile = (email: string) => {
    const updated = savedProfiles.filter(p => p.email !== email)
    localStorage.setItem('valrat_profiles', JSON.stringify(updated))
    setSavedProfiles(updated)
    
    if (currentUser?.email === email) {
      logoutCurrent()
    }
  }

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      currentUser, 
      savedProfiles, 
      login, 
      switchProfile, 
      logoutCurrent, 
      removeProfile 
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  return context
}