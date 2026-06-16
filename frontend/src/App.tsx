import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from './services/supabase';
import api from './services/api';
import { Login } from './pages/Login';
import { Home } from './pages/Home';
import { Catalog } from './pages/Catalog';
import { AdminDashboard } from './pages/AdminDashboard';
import { Navbar } from './components/Navbar';
import { Loader2 } from 'lucide-react';

function App() {
  const [session, setSession] = useState<any>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  const checkAdminStatus = (session: any) => {
    // Verifica admin via app_metadata do Supabase (contido no JWT) - operação síncrona
    const adminStatus = session?.user?.app_metadata?.is_admin || false;
    setIsAdmin(adminStatus);
  };

  useEffect(() => {
    const initAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setSession(session);
        if (session) {
          checkAdminStatus(session);
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: any, session: any) => {
      setSession(session);
      if (_event === 'SIGNED_OUT') {
        setIsAdmin(false);
      } else if (_event === 'SIGNED_IN' || _event === 'INITIAL_SESSION') {
        if (session) checkAdminStatus(session);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true } as any}>
      <div className="min-h-screen bg-gray-50">
        <Navbar isAdmin={isAdmin} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route 
            path="/login" 
            element={
              session ? 
              <Navigate to={isAdmin ? "/admin" : "/"} /> : 
              <Login />
            } 
          />
          <Route path="/admin" element={isAdmin ? <AdminDashboard /> : <Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;