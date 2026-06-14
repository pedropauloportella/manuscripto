import React from 'react';
import { supabase } from '../services/supabase';
import { GraduationCap, Mail } from 'lucide-react';

export const Login = () => {
  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin }
    });
  };

  const handleOrcidLogin = () => {
    // O ORCID é processado pelo nosso backend FastAPI
    const clientId = "APP-XXXXXXXXXXXXXXXX"; // Deve vir de config ou env
    const redirectUri = encodeURIComponent("http://localhost:8000/api/v1/auth/orcid/callback");
    window.location.href = `https://orcid.org/oauth/authorize?client_id=${clientId}&response_type=code&scope=/authenticate&redirect_uri=${redirectUri}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">Manuscripto</h2>
          <p className="mt-2 text-sm text-gray-600">Gestão Editorial Acadêmica</p>
        </div>
        
        <div className="mt-8 space-y-4">
          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <img className="h-5 w-5 mr-2" src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" />
            Entrar com Google
          </button>

          <button
            onClick={handleOrcidLogin}
            className="w-full flex items-center justify-center px-4 py-2 border border-green-600 rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
          >
            <GraduationCap className="h-5 w-5 mr-2" />
            Entrar com ORCID
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300"></div></div>
            <div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-gray-500">Ou use email</span></div>
          </div>

          <form className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <button className="w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
              <Mail className="h-5 w-5 mr-2" />
              Entrar com Link Mágico
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};