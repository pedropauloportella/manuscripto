import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Plus, Book, Trash2, LayoutDashboard, Loader2, Users, ShieldAlert, Activity } from 'lucide-react';

interface Publicacao {
  id: string;
  titulo: string;
  tipo: string;
}

export const AdminDashboard = () => {
  const [publicacoes, setPublicacoes] = useState<Publicacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPub, setNewPub] = useState({ titulo: '', descricao: '', tipo: 'livro' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/publications/');
      setPublicacoes(res.data);
    } catch (error) {
      const err = error as any;
      console.error("Erro ao carregar dados administrativos:", err);
      if (err.response?.status === 403) {
        alert("Acesso negado: Você não tem permissão para visualizar ou gerenciar publicações.");
      } else if (err.response?.status === 401) {
        alert("Sessão inválida ou expirada. Por favor, faça login novamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePub = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/publications/', newPub);
      setNewPub({ titulo: '', descricao: '', tipo: 'livro' });
      fetchData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro desconhecido";
      console.error("Erro ao criar publicação:", errorMessage);
      
      if (error.response?.status === 403) alert("Acesso negado: Sem privilégios de administrador.");
      else if (error.response?.status === 401) alert(`Sessão inválida: ${errorMessage}`);
      else alert(`Erro ao criar publicação: ${errorMessage}`);
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center h-[60vh]">
      <Loader2 className="animate-spin h-10 w-10 text-indigo-600" />
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <header className="mb-10">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 flex items-center">
            <LayoutDashboard className="mr-3 h-8 w-8 text-indigo-600" /> Painel de Controle
          </h1>
          <p className="text-gray-600 mt-1">Visão geral do sistema Manuscripto.</p>
        </div>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="bg-indigo-600 p-6 rounded-2xl text-white shadow-lg shadow-indigo-200">
            <div className="flex items-center justify-between">
              <Book className="h-8 w-8 opacity-80" />
              <span className="text-2xl font-bold">{publicacoes.length}</span>
            </div>
            <p className="mt-2 font-medium">Obras Cadastradas</p>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Usuários Ativos</p>
              <p className="text-2xl font-bold text-gray-900">--</p>
            </div>
            <Users className="h-8 w-8 text-indigo-500 opacity-20" />
          </div>
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Status do Sistema</p>
              <p className="text-lg font-bold text-green-600">Operacional</p>
            </div>
            <Activity className="h-8 w-8 text-green-500 opacity-20" />
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulário de Criação */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Plus className="mr-2 h-5 w-5 text-indigo-600" /> Nova Publicação
            </h2>
            <form onSubmit={handleCreatePub} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Título</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                  value={newPub.titulo}
                  onChange={e => setNewPub({...newPub, titulo: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select 
                  className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                  value={newPub.tipo}
                  onChange={e => setNewPub({...newPub, tipo: e.target.value})}
                >
                  <option value="livro">Livro</option>
                  <option value="artigo">Artigo</option>
                  <option value="capitulo">Capítulo</option>
                </select>
              </div>
              <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-lg font-bold hover:bg-indigo-700 transition-colors">
                Criar Obra
              </button>
            </form>
          </div>
        </div>

        {/* Lista de Publicações */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Book className="mr-2 h-5 w-5 text-indigo-600" /> Obras Ativas
          </h2>
          {publicacoes.map(pub => (
            <div key={pub.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:border-indigo-200 transition-colors">
              <div className="flex items-center">
                <div className="bg-indigo-50 p-2 rounded-lg mr-4">
                  <Book className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">{pub.titulo}</h3>
                  <span className="text-xs uppercase font-semibold text-gray-400">{pub.tipo}</span>
                </div>
              </div>
              <button className="text-red-400 hover:text-red-600 p-2"><Trash2 className="h-5 w-5" /></button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};