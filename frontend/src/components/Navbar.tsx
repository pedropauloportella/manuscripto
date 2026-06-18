import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase } from '../services/supabase';
import { LogOut, Book, LogIn, LayoutDashboard, User } from 'lucide-react';

export const Navbar = ({ isAdmin }: { isAdmin: boolean }) => {
  const navigate = useNavigate();
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }: any) => {
      setSession(session);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: any, session: any) => {
      setSession(session);
    });
    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
              Manuscripto
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/catalog" className="text-gray-600 hover:text-indigo-600 p-2 transition-all hover:scale-110" title="Catálogo">
              <Book className="h-6 w-6" />
            </Link>
            {isAdmin && (
              <Link to="/admin" className="text-indigo-600 hover:text-indigo-800 p-2 transition-all hover:rotate-12" title="Painel Admin">
                <LayoutDashboard className="h-6 w-6" />
              </Link>
            )}
            {session ? (
              <>
                <Link to={`/profile/${session.user.id}`} className="text-gray-500 hover:text-indigo-600 p-2 transition-all hover:scale-110" title="Meu Perfil">
                  <User className="h-6 w-6" />
                </Link>
                <button onClick={handleLogout} className="text-gray-500 hover:text-red-600 p-2 transition-colors" title="Sair">
                  <LogOut className="h-5 w-5" />
                </button>
              </>
            ) : (
              <Link to="/login" className="flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
                <LogIn className="h-4 w-4 mr-2" /> Entrar
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};