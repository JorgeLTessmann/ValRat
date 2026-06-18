const BASE_URL = 'https://valrat.onrender.com';

// Função auxiliar para garantir que a URL não tenha barras duplicadas por acidente
const buildUrl = (endpoint: string): string => {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${BASE_URL}${cleanEndpoint}`;
};

const getHeaders = (email: string) => {
  // Garante que envia uma string limpa ou vazia, sem quebrar
  const cleanEmail = email && typeof email === 'string' ? email.trim() : '';
  
  return {
    'Content-Type': 'application/json',
    'X-User-Email': cleanEmail,
  };
};

export const fetchPortfolioData = async (endpoint: string, email: string) => {
  if (!email) throw new Error("Email não fornecido para carregar dados.");
  
  const res = await fetch(buildUrl(endpoint), {
    method: 'GET',
    headers: getHeaders(email),
  });

  if (!res.ok) {
    throw new Error(`Erro ao carregar carteira completa: ${res.status}`);
  }
  return res.json();
};

export const fetchPortfolioResumo = async (endpoint: string, email: string) => {
  if (!email) throw new Error("Email não fornecido para carregar resumo.");
  
  const res = await fetch(buildUrl(endpoint), {
    method: 'GET',
    headers: getHeaders(email),
  });

  if (!res.ok) {
    throw new Error(`Erro ao carregar resumo da carteira: ${res.status}`);
  }
  return res.json();
};

export const fetchHistorico = async (endpoint: string, email: string) => {
  if (!email) throw new Error("Email não fornecido para carregar histórico.");

  const res = await fetch(buildUrl(endpoint), {
    method: 'GET',
    headers: getHeaders(email),
  });

  if (!res.ok) {
    throw new Error(`Erro ao carregar histórico: ${res.status}`);
  }
  return res.json();
};

export const fetchBenchmarks = async (endpoint: string, email: string) => {
  if (!email) throw new Error("Email não fornecido para carregar benchmarks.");

  const res = await fetch(buildUrl(endpoint), {
    method: 'GET',
    headers: getHeaders(email),
  });

  if (!res.ok) {
    throw new Error(`Erro ao carregar benchmarks: ${res.status}`);
  }
  return res.json();
};

export const loginUsuario = async (dados: any) => {
  const res = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.erro || 'Falha ao realizar login');
  }
  return res.json();
};

export const cadastrarUsuario = async (dados: any) => {
  const res = await fetch(`${BASE_URL}/cadastro`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.erro || 'Falha ao realizar cadastro');
  }
  return res.json();
};