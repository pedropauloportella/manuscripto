import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from './services/supabase';
import api from './services/api';
import { Login } from './pages/Login';
import { Home } from './pages/Home';
import { Catalog } from './pages/Catalog';
import { Profile } from './pages/Profile';
import { NotificationProvider } from './context/NotificationContext';
import { AdminDashboard } from './pages/AdminDashboard';
import { Navbar } from './components/Navbar';
import { Loader2 } from 'lucide-react';

function App() {
  const [session, setSession] = useState<any>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userRole, setUserRole] = useState<string>("autor");
  const [loading, setLoading] = useState(true);

  const checkAuthStatus = (session: any) => {
    // Verifica admin via app_metadata do Supabase (contido no JWT) - operação síncrona
    const adminStatus = session?.user?.app_metadata?.is_admin || false;
    const role = session?.user?.app_metadata?.role || "autor";
    setIsAdmin(adminStatus);
    setUserRole(role);
  };

  useEffect(() => {
    const initAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setSession(session);
        if (session) {
          checkAuthStatus(session);
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
        setUserRole("autor");
      } else if (_event === 'SIGNED_IN' || _event === 'INITIAL_SESSION') {
        if (session) checkAuthStatus(session);
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
    <NotificationProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true } as any}>
        <div className="min-h-screen bg-gray-50">
          <Navbar isAdmin={isAdmin || userRole === "editor"} />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/catalog" element={<Catalog />} />
            <Route path="/profile/:id" element={<Profile />} />
            <Route 
              path="/login" 
              element={
                session ? 
                <Navigate to={isAdmin ? "/admin" : "/"} /> : 
                <Login />
              } 
            />
            <Route path="/admin" element={(isAdmin || userRole === "editor") ? <AdminDashboard /> : <Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </NotificationProvider>
  );
}

export default App;