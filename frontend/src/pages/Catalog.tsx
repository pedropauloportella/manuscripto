import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { supabase } from '../services/supabase';
import { useNotification } from '../context/NotificationContext';
import { Book, ShoppingCart, Loader2, Info, Calendar, BadgeCheck, FlaskConical, Clock, User, FileText } from 'lucide-react';

interface Vaga {
  id: string;
  titulo: string;
  descricao: string;
  preco: number;
  quantidade_disponivel: number;
  data_encerramento: string;
  pre_requisitos: string;
  publicacao: {
    titulo: string;
    tipo: string;
    resumo: string;
    area_conhecimento: string;
    tem_doi: boolean;
    tem_isbn: boolean;
    tem_issn: boolean;
    criador?: {
      nome_completo?: string;
      grau_formacao?: string;
    };
  }
}

export const Catalog = () => {
  const [vagas, setVagas] = useState<Vaga[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchasingId, setPurchasingId] = useState<string | null>(null);
  const { showNotification } = useNotification();

  useEffect(() => {
    const fetchVagas = async () => {
      try {
        const response = await api.get('/catalog/vagas');
        setVagas(response.data);
      } catch (error: any) {
        console.error("Erro ao carregar catálogo", error); // Manter console.error para depuração
        showNotification("Erro ao carregar o catálogo de vagas.", 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchVagas();
  }, []);

  const handlePurchase = async (vagaId: string) => {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      showNotification("Você precisa estar logado para adquirir uma vaga.", 'info');
      return;
    }

    setPurchasingId(vagaId);
    try {
      const response = await api.post(`/payments/checkout/${vagaId}`);
      window.location.href = response.data.init_point; // Redireciona para o MercadoPago
    } catch (error) {
      showNotification("Não foi possível iniciar a compra. Tente novamente mais tarde.", 'error');
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
              {vaga.imagem_url && (
                <img src={vaga.imagem_url} alt={vaga.titulo} className="w-full h-40 object-cover rounded-lg mb-4" />
              )}

              <div className="flex justify-between items-start mb-4">
                <div className="bg-indigo-50 p-2 rounded-lg text-indigo-600">
                  <Book className="h-6 w-6" />
                </div>

                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded uppercase">
                  {vaga.publicacao.tipo}
                </span>
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-1 line-clamp-2" title={vaga.publicacao.titulo}>
                {vaga.publicacao.titulo}
              </h3>
              <p className="text-sm font-semibold text-indigo-600 mb-4">
                Vaga: {vaga.titulo}
              </p>

              {vaga.publicacao.resumo && (
                <div className="mb-4 bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <p className="text-xs font-bold text-gray-500 uppercase mb-1 flex items-center">
                    <FileText className="h-3 w-3 mr-1" /> Resumo da Obra
                  </p>
                  <p className="text-gray-600 text-xs line-clamp-3 italic">{vaga.publicacao.resumo}</p>
                </div>
              )}

              <div className="space-y-2 text-xs text-gray-600 mb-4">
                <p className="flex items-center"><User className="h-4 w-4 mr-2 text-gray-400" /> <span className="font-medium text-gray-900">Organizador:</span>&nbsp;{vaga.publicacao.criador?.nome_completo || "Editor Editorial"}</p>
                <p className="flex items-center"><FlaskConical className="h-4 w-4 mr-2 text-gray-400" /> <span className="font-medium text-gray-900">Área:</span>&nbsp;{vaga.publicacao.area_conhecimento || "Geral"}</p>
                <p className="flex items-center"><Info className="h-4 w-4 mr-2 text-gray-400" /> <span className="font-medium text-gray-900">Pré-requisitos:</span>&nbsp;{vaga.pre_requisitos || "Qualquer nível acadêmico"}</p>
                <p className="flex items-center"><Clock className="h-4 w-4 mr-2 text-amber-500" /> <span className="font-medium text-gray-900">Adesão até:</span>&nbsp;{vaga.data_encerramento ? new Date(vaga.data_encerramento).toLocaleDateString('pt-BR') : "Fluxo contínuo"}</p>
                <p className="flex items-center"><Calendar className="h-4 w-4 mr-2 text-indigo-500" /> <span className="font-medium text-gray-900">Previsão Lançamento:</span>&nbsp;{vaga.publicacao.data_prevista_publicacao ? new Date(vaga.publicacao.data_prevista_publicacao).toLocaleDateString('pt-BR') : "A definir"}</p>
              </div>

              <div className="flex flex-wrap gap-1.5 mb-4">
                {vaga.publicacao.tem_doi && <span className="text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-200">DOI Indexado</span>}
                {vaga.publicacao.tem_isbn && <span className="text-[10px] font-bold bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-200">ISBN</span>}
                {vaga.publicacao.tem_issn && <span className="text-[10px] font-bold bg-pink-50 text-pink-700 px-2 py-0.5 rounded border border-pink-200">ISSN</span>}
              </div>

              <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded-lg flex justify-between">
                <span>Vagas Totais: <strong>{vaga.quantidade_total}</strong></span>
                <span>Preenchidas: <strong>{vaga.quantidade_total - vaga.quantidade_disponivel}</strong></span>
                <span className="text-green-600 font-bold">Disponíveis: {vaga.quantidade_disponivel}</span>
              </div>
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