# Manuscripto Frontend

Interface do sistema de gestão editorial acadêmica.

## Tecnologias

- **React 18** + **TypeScript**
- **Vite** (Build Tool)
- **Tailwind CSS** (Estilização)
- **Supabase Auth Helper** (Autenticação)
- **Axios** (Comunicação com API Backend)

## Configuração

Crie um arquivo `.env` na pasta `frontend/` com:

```env
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-anon-key
VITE_API_URL=http://localhost:8000/api/v1
```

## Como Rodar

```bash
npm install
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`.
