import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { supabase } from '../services/supabase';
import { Book, ShoppingCart, Loader2, Info } from 'lucide-react';

interface Vaga {
  id: string;
  titulo: string;
  descricao: string;
  preco: number;
  quantidade_disponivel: number;
}

export const Catalog = () => {
  const [vagas, setVagas] = useState<Vaga[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchasingId, setPurchasingId] = useState<string | null>(null);

  useEffect(() => {
    const fetchVagas = async () => {
      try {
        const response = await api.get('/catalog/vagas');
        setVagas(response.data);
      } catch (error) {
        console.error("Erro ao carregar catálogo", error);
      } finally {
        setLoading(false);
      }
    };
    fetchVagas();
  }, []);

  const handlePurchase = async (vagaId: string) => {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      alert("Você precisa estar logado para adquirir uma vaga.");
      return;
    }

    setPurchasingId(vagaId);
    try {
      const response = await api.post(`/payments/checkout/${vagaId}`);
      window.location.href = response.data.init_point;
    } catch (error) {
      alert("Não foi possível iniciar a compra. Tente novamente mais tarde.");
    } finally {
      setPurchasingId(null);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-[60vh]"><Loader2 className="animate-spin h-10 w-10 text-indigo-600" /></div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Catálogo de Coautoria</h1>
        <p className="mt-4 text-lg text-gray-600">Garanta sua participação em publicações acadêmicas de alto impacto.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {vagas.map((vaga) => (
          <div key={vaga.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col hover:shadow-md transition-shadow">
            <div className="p-6 flex-grow">
              <div className="flex justify-between items-start mb-4">
                <div className="bg-indigo-50 p-2 rounded-lg text-indigo-600"><Book className="h-6 w-6" /></div>
                <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-1 rounded-full uppercase">Disponível</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{vaga.titulo}</h3>
              <p className="text-gray-600 text-sm line-clamp-3">{vaga.descricao || "Participe desta obra científica como coautor."}</p>
            </div>
            <div className="p-6 bg-indigo-50/50 border-t border-indigo-100 flex items-center justify-between">
              <div className="text-xl font-bold text-gray-900">R$ {Number(vaga.preco).toFixed(2)}</div>
              <button onClick={() => handlePurchase(vaga.id)} disabled={purchasingId !== null} className="flex items-center px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
                {purchasingId === vaga.id ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : <ShoppingCart className="h-4 w-4 mr-2" />}
                {purchasingId === vaga.id ? "Processando..." : "Comprar"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};