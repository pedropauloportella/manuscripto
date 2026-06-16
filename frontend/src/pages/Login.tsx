import React, { useState } from 'react';
import { supabase } from '../services/supabase';
import api from '../services/api';
import { GraduationCap, Mail, Lock, UserPlus, LogIn, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin }
    });
  };

  const handleOrcidLogin = () => {
    const clientId = import.meta.env.VITE_ORCID_CLIENT_ID || "APP-XXXXXXXXXXXXXXXX";
    const redirectUri = encodeURIComponent(`${import.meta.env.VITE_API_URL}/auth/orcid/callback`);
    window.location.href = `https://orcid.org/oauth/authorize?client_id=${clientId}&response_type=code&scope=/authenticate&redirect_uri=${redirectUri}`;
  };

  const handleEmailPasswordAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    if (isSignUp) {
      // Lógica de Cadastro
      const { error } = await supabase.auth.signUp({
        email,
        password,
      });
      if (error) alert(error.message);
      else alert("Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta.");
    } else {
      try {
        // Autentica diretamente no Supabase
        const { data: authData, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) throw error;

        // Verifica se o usuário é admin via metadata do Supabase
        if (authData.user?.app_metadata?.is_admin) {
          navigate('/admin');
        } else {
          navigate('/');
        }

      } catch (error: any) {
        console.error("Erro detalhado no login:", error);
        const errorMessage = 
          error.response?.data?.detail || 
          error.message || 
          (error.error_description) || // Para erros vindos do Supabase
          "Erro inesperado na autenticação";
        alert(`Falha no login: ${errorMessage}`);
      }
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">Manuscripto</h2>
          <p className="mt-2 text-sm text-gray-600 font-medium">Gestão Editorial Acadêmica</p>
        </div>
        <div className="mt-8 space-y-4">
          <button onClick={handleGoogleLogin} className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors">
            <img className="h-5 w-5 mr-2" src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" /> Entrar com Google
          </button>
          <button onClick={handleOrcidLogin} className="w-full flex items-center justify-center px-4 py-2 border border-green-600 rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 transition-colors">
            <GraduationCap className="h-5 w-5 mr-2" /> Entrar com ORCID
          </button>
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300"></div></div>
            <div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-gray-500">Ou use email</span></div>
          </div>
          <form className="space-y-4" onSubmit={handleEmailPasswordAuth}>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <button type="submit" disabled={loading} className="w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50">
              {loading ? 
                <Loader2 className="animate-spin h-5 w-5" /> : 
                (isSignUp ? <><UserPlus className="h-5 w-5 mr-2" /> Criar Conta</> : <><LogIn className="h-5 w-5 mr-2" /> Entrar</>)
              }
            </button>
          </form>
          <div className="text-center mt-4">
            <button 
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-sm text-indigo-600 hover:text-indigo-500 font-medium transition-colors"
            >
              {isSignUp ? "Já tem uma conta? Entre aqui" : "Não tem uma conta? Cadastre-se gratuitamente"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};