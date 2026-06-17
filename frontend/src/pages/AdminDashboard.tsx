import React, { useState, useEffect } from 'react';
import api from '../services/api';
import axios from 'axios'; // Importar axios para a chamada de health check
import { Plus, Book, Trash2, LayoutDashboard, Loader2, Users, ShieldAlert, Activity, Database, Check, X } from 'lucide-react';
import { useNotification } from '../context/NotificationContext';

interface Publicacao {
  id: string;
  titulo: string;
  tipo: string;
}

interface Vaga {
  id: string;
  titulo: string;
  preco: number;
  quantidade_total: number;
  quantidade_disponivel: number;
  ativa: boolean;
}

interface User {
  id: string;
  email: string;
  nome_completo?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export const AdminDashboard = () => {
  const [publicacoes, setPublicacoes] = useState<Publicacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPub, setNewPub] = useState({ titulo: '', descricao: '', tipo: 'livro' });
  const [editingPub, setEditingPub] = useState<Publicacao | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'publications' | 'users' | 'settings'>('overview');
  const [backendStatus, setBackendStatus] = useState<'operational' | 'degraded' | 'down'>('degraded');
  const [databaseStatus, setDatabaseStatus] = useState<'operational' | 'degraded' | 'down'>('degraded');
  const [frontendStatus, setFrontendStatus] = useState<'operational' | 'degraded' | 'down'>('operational'); // Frontend é operacional se o componente está renderizado
  
  const [selectedPubVagas, setSelectedPubVagas] = useState<string | null>(null);
  const [vagas, setVagas] = useState<Vaga[]>([]);
  const [newVaga, setNewVaga] = useState({ titulo: '', preco: 0, quantidade_total: 1 });
  const [editingVaga, setEditingVaga] = useState<Vaga | null>(null);

  const { showNotification } = useNotification();

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      // Carrega ambos em paralelo para melhor performance
      await Promise.all([fetchData(), fetchUsers(), checkSystemHealth()]);
      setLoading(false);
    };
    loadInitialData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/publications/');
      setPublicacoes(res.data);
    } catch (error) {
      const err = error as any;
      console.error("Erro ao carregar dados administrativos:", err);
      if (err.response?.status === 403) {
        showNotification("Acesso negado: Você não tem permissão para visualizar publicações.", 'error');
      } else if (err.response?.status === 401) {
        showNotification("Sessão inválida ou expirada. Por favor, faça login novamente.", 'error');
      }
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users/');
      setUsers(res.data);
    } catch (error) {
      const err = error as any;
      console.error("Erro ao carregar usuários:", err);
      if (err.response?.status === 403) {
        showNotification("Acesso negado: Você não tem permissão para visualizar usuários.", 'error');
      } else if (err.response?.status === 401) {
        showNotification("Sessão inválida ou expirada. Por favor, faça login novamente.", 'error');
      }
    }
  };

  const handleUpdatePublication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPub) return;
    try {
      await api.put(`/publications/${editingPub.id}`, editingPub);
      showNotification("Publicação atualizada com sucesso!", "success");
      setEditingPub(null);
      fetchData();
    } catch (error: any) {
      showNotification("Erro ao atualizar publicação.", "error");
    }
  };

  const fetchVagas = async (pubId: string) => {
    try {
      const res = await api.get(`/publications/${pubId}/vagas`);
      setVagas(res.data);
      setSelectedPubVagas(pubId);
    } catch (error) {
      showNotification("Erro ao carregar vagas desta publicação.", "error");
    }
  };

  const handleCreateVaga = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPubVagas) return;
    try {
      await api.post(`/publications/${selectedPubVagas}/vagas`, newVaga);
      showNotification("Vaga de coautoria criada!", "success");
      setNewVaga({ titulo: '', preco: 0, quantidade_total: 1 });
      fetchVagas(selectedPubVagas);
    } catch (error) {
      showNotification("Erro ao criar vaga.", "error");
    }
  };

  const handleUpdateVaga = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingVaga) return;
    try {
      await api.put(`/publications/vagas/${editingVaga.id}`, editingVaga);
      showNotification("Vaga atualizada com sucesso!", "success");
      setEditingVaga(null);
      if (selectedPubVagas) fetchVagas(selectedPubVagas);
    } catch (error) {
      showNotification("Erro ao atualizar vaga.", "error");
    }
  };

  const handleDeleteVaga = async (vagaId: string) => {
    if (!window.confirm("Excluir esta oferta de vaga?")) return;
    try {
      await api.delete(`/publications/vagas/${vagaId}`);
      if (selectedPubVagas) fetchVagas(selectedPubVagas);
      showNotification("Vaga removida.", "success");
    } catch (error) {
      showNotification("Erro ao remover vaga.", "error");
    }
  };

  const checkSystemHealth = async () => {
    try {
      // O endpoint /health está na raiz da API, não sob /api/v1.
      // Usamos import.meta.env.VITE_API_URL e removemos '/api/v1' para obter a base.
      const healthUrl = import.meta.env.VITE_API_URL.replace('/api/v1', '/health');
      const backendRes = await axios.get(healthUrl); // Usar axios diretamente para o endpoint raiz

      if (backendRes.data.status === 'ok') {
        setBackendStatus('operational');
        setDatabaseStatus('operational'); // Status do banco de dados vem da checagem do backend
      } else {
        setBackendStatus('degraded');
        setDatabaseStatus('degraded');
      }
    } catch (error) {
      console.error("Erro ao verificar saúde do backend:", error);
      setBackendStatus('down');
      setDatabaseStatus('down');
      showNotification("Backend ou banco de dados indisponível.", 'error');
    }
    setFrontendStatus('operational'); // Frontend é operacional se este componente está renderizado
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
      
      if (error.response?.status === 403) showNotification("Acesso negado: Sem privilégios de administrador.", 'error');
      else if (error.response?.status === 401) showNotification(`Sessão inválida: ${errorMessage}`, 'error');
      else showNotification(`Erro ao criar publicação: ${errorMessage}`, 'error');
    }
  };

  const handleDeletePublication = async (pubId: string) => {
    if (!window.confirm("Tem certeza que deseja excluir esta publicação?")) return; // Manter confirm para ações destrutivas
    try {
      await api.delete(`/publications/${pubId}`);
      fetchData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro ao excluir publicação.";
      console.error("Erro ao excluir publicação:", errorMessage);
      showNotification(`Erro ao excluir publicação: ${errorMessage}`, 'error'); // Substituir alert por showNotification
    }
  };
  
  const handleToggleSuperuser = async (userId: string, currentStatus: boolean) => {
    if (!window.confirm(`Tem certeza que deseja ${currentStatus ? 'remover' : 'conceder'} privilégios de administrador para este usuário?`)) return;
    try {
      await api.put(`/users/${userId}/toggle-superuser`);
      fetchUsers();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro ao alterar status de superuser.";
      console.error("Erro ao alterar status de superuser:", errorMessage); // Manter console.error para depuração
      showNotification(`Erro: ${errorMessage}`, 'error');
    }
  };

  const handleToggleActive = async (userId: string, currentStatus: boolean) => {
    if (!window.confirm(`Tem certeza que deseja ${currentStatus ? 'desativar' : 'ativar'} este usuário?`)) return;
    try {
      await api.put(`/users/${userId}/toggle-active`);
      fetchUsers();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro ao alterar status de ativo.";
      console.error("Erro ao alterar status de ativo:", errorMessage); // Manter console.error para depuração
      showNotification(`Erro: ${errorMessage}`, 'error');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!window.confirm("Tem certeza que deseja excluir este usuário permanentemente?")) return;
    // Implementar lógica de exclusão de usuário
    showNotification("Funcionalidade de exclusão de usuário ainda não implementada.", 'info');
  }

  const handleSeedData = async () => {
    if (!window.confirm("Tem certeza que deseja popular o banco de dados com dados fictícios? Isso pode sobrescrever dados existentes.")) return;
    setLoading(true);
    try {
      await api.post('/users/seed-fictitious');
      showNotification("Dados fictícios criados com sucesso!", 'success');
      fetchData(); // Atualiza publicações
      fetchUsers(); // Atualiza usuários
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro ao popular o banco de dados.";
      console.error("Erro ao popular dados:", errorMessage);
      showNotification(`Erro: ${errorMessage}`, 'error'); // Substituir alert por showNotification
    } finally {
      setLoading(false);
    }
  };

  const handleClearData = async () => {
    if (!window.confirm("Tem certeza que deseja LIMPAR TODOS os dados fictícios? Esta ação é irreversível e removerá usuários, publicações e vagas.")) return; // Manter confirm para ações destrutivas
    setLoading(true);
    try {
      await api.delete('/users/clear-fictitious');
      showNotification("Dados fictícios removidos com sucesso!", 'success');
      fetchData(); // Atualiza publicações
      fetchUsers(); // Atualiza usuários
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Erro ao limpar o banco de dados.";
      console.error("Erro ao limpar dados:", errorMessage); // Manter console.error para depuração
      showNotification(`Erro: ${errorMessage}`, 'error');
    } finally {
      setLoading(false);
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
          <h1 className="text-4xl font-extrabold text-gray-900 flex items-center">
            <LayoutDashboard className="mr-3 h-8 w-8 text-indigo-600" /> Painel de Controle
          </h1>
          <p className="text-gray-600 mt-1">Visão geral do sistema Manuscripto.</p>
        </div>

        {/* Navigation Tabs */}
        <div className="mt-8 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('overview')}
              className={`${activeTab === 'overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Visão Geral
            </button>
            <button
              onClick={() => setActiveTab('publications')}
              className={`${activeTab === 'publications' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Publicações
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`${activeTab === 'users' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Usuários
            </button>
            {/* Adicionar mais tabs conforme necessário */}
          </nav>
        </div>
        
        {/* Quick Stats */}
        {/* System Health */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-indigo-600" /> Saúde do Sistema
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <span className={`h-3 w-3 rounded-full ${frontendStatus === 'operational' ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <p className="text-gray-700">Frontend: <span className="font-medium">{frontendStatus === 'operational' ? 'Operacional' : 'Indisponível'}</span></p>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`h-3 w-3 rounded-full ${backendStatus === 'operational' ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <p className="text-gray-700">Backend: <span className="font-medium">{backendStatus === 'operational' ? 'Operacional' : 'Indisponível'}</span></p>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`h-3 w-3 rounded-full ${databaseStatus === 'operational' ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <p className="text-gray-700">Banco de Dados: <span className="font-medium">{databaseStatus === 'operational' ? 'Conectado' : 'Desconectado'}</span></p>
            </div>
          </div>
          { (backendStatus === 'down' || databaseStatus === 'down') && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md flex items-center">
              <ShieldAlert className="h-5 w-5 mr-2" />
              <span>Atenção: Problemas de conexão com o backend ou banco de dados.</span>
            </div>
          )}
        </div>
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
              <p className="text-gray-500 text-sm font-medium">Total de Usuários</p>
              <p className="text-2xl font-bold text-gray-900">{users.length}</p>
            </div>
            <Users className="h-8 w-8 text-indigo-500 opacity-20" /> {/* TODO: Filtrar por ativos */}
          </div>
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Status do Sistema</p>
              <p className={`text-lg font-bold ${
                backendStatus === 'operational' && databaseStatus === 'operational' 
                ? 'text-green-600' 
                : 'text-red-600'
              }`}>
                {backendStatus === 'operational' && databaseStatus === 'operational' ? 'Operacional' : 'Instável'}
              </p>
            </div>
            <Activity className={`h-8 w-8 opacity-20 ${
              backendStatus === 'operational' && databaseStatus === 'operational' 
              ? 'text-green-500' 
              : 'text-red-500'
            }`} />
          </div>
        </div>
      </header>

      {/* Seeding Controls */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <Database className="mr-2 h-5 w-5 text-indigo-600" /> Ferramentas de Desenvolvimento
        </h2>
        <p className="text-gray-600 mb-4">
          Use estas ferramentas para popular ou limpar o banco de dados com dados fictícios.
          **Cuidado:** A limpeza removerá todos os dados das tabelas de usuários, publicações, vagas, etc.
        </p>
        <div className="flex space-x-4">
          <button 
            onClick={handleSeedData}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-bold hover:bg-green-700 transition-colors flex items-center justify-center"
          >
            <Plus className="h-5 w-5 mr-2" /> Popular Banco de Dados
          </button>
          <button 
            onClick={handleClearData}
            className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg font-bold hover:bg-red-700 transition-colors flex items-center justify-center"
          >
            <Trash2 className="h-5 w-5 mr-2" /> Limpar Dados Fictícios
          </button>
        </div>
      </div>

      {activeTab === 'overview' && (
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
                <div className="flex items-center flex-grow">
                  <div className="bg-indigo-50 p-2 rounded-lg mr-4">
                    <Book className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900">{pub.titulo}</h3>
                    <span className="text-xs uppercase font-semibold text-gray-400">{pub.tipo}</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button onClick={() => setEditingPub(pub)} className="text-indigo-600 hover:bg-indigo-50 p-2 rounded-lg transition-colors">
                    <Activity className="h-5 w-5" /> {/* Ícone representativo para Edit */}
                  </button>
                  <button onClick={() => handleDeletePublication(pub.id)} className="text-red-400 hover:text-red-600 p-2">
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'publications' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold flex items-center">
              <Book className="mr-2 h-6 w-6 text-indigo-600" /> Todas as Publicações
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {publicacoes.map(pub => (
              <div key={pub.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 flex items-center justify-between border-b border-gray-50">
                  <div className="flex items-center">
                    <div className="bg-indigo-100 p-3 rounded-xl mr-4">
                      <Book className="h-6 w-6 text-indigo-600" />
                    </div>
                    <div>
                      {editingPub?.id === pub.id ? (
                        <form onSubmit={handleUpdatePublication} className="flex items-center space-x-2">
                          <input 
                            className="border rounded px-2 py-1 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={editingPub.titulo}
                            onChange={e => setEditingPub({...editingPub, titulo: e.target.value})}
                          />
                          <button type="submit" className="text-green-600 font-bold text-sm">Salvar</button>
                          <button type="button" onClick={() => setEditingPub(null)} className="text-gray-400 text-sm">Cancelar</button>
                        </form>
                      ) : (
                        <>
                          <h3 className="text-lg font-bold text-gray-900">{pub.titulo}</h3>
                          <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded uppercase">{pub.tipo}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => fetchVagas(pub.id)}
                      className="flex items-center px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                    >
                      <Plus className="h-4 w-4 mr-1" /> Vagas
                    </button>
                    <button onClick={() => setEditingPub(pub)} className="p-2 text-gray-400 hover:text-indigo-600">
                      <Activity className="h-5 w-5" />
                    </button>
                    <button onClick={() => handleDeletePublication(pub.id)} className="p-2 text-gray-400 hover:text-red-500">
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {selectedPubVagas === pub.id && (
                  <div className="bg-gray-50 p-6 border-t border-gray-100">
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="font-bold text-gray-700 flex items-center">
                        <Users className="h-4 w-4 mr-2" /> Vagas de Coautoria
                      </h4>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {vagas.map(v => (
                        <div key={v.id} className="bg-white p-3 rounded-xl border border-gray-200 flex justify-between items-center">
                          {editingVaga?.id === v.id ? (
                            <form onSubmit={handleUpdateVaga} className="flex flex-col space-y-2 w-full">
                              <input 
                                className="text-sm border rounded px-2 py-1"
                                value={editingVaga.titulo}
                                onChange={e => setEditingVaga({...editingVaga, titulo: e.target.value})}
                              />
                              <div className="flex space-x-2">
                                <input 
                                  type="number"
                                  className="text-sm border rounded px-2 py-1 w-24"
                                  value={editingVaga.preco}
                                  onChange={e => setEditingVaga({...editingVaga, preco: Number(e.target.value)})}
                                />
                                <button type="submit" className="text-green-600 font-bold text-xs uppercase">Salvar</button>
                                <button type="button" onClick={() => setEditingVaga(null)} className="text-gray-400 text-xs uppercase">Cancelar</button>
                              </div>
                            </form>
                          ) : (
                            <>
                              <div>
                                <p className="font-semibold text-sm">{v.titulo}</p>
                                <p className="text-xs text-gray-500">
                                  R$ {Number(v.preco).toFixed(2)} | {v.quantidade_disponivel}/{v.quantidade_total} vagas
                                </p>
                              </div>
                              <div className="flex space-x-2">
                                <button onClick={() => setEditingVaga(v)} className="p-1 text-gray-400 hover:text-indigo-600 transition-colors">
                                  <Activity className="h-4 w-4" />
                                </button>
                                <button onClick={() => handleDeleteVaga(v.id)} className="p-1 text-gray-400 hover:text-red-500 transition-colors">
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>

                    <form onSubmit={handleCreateVaga} className="bg-white p-4 rounded-xl border border-dashed border-gray-300 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                      <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1 uppercase">Título da Vaga</label>
                        <input 
                          className="w-full text-sm border rounded p-2" 
                          placeholder="Ex: Coautor Metodologia"
                          value={newVaga.titulo}
                          onChange={e => setNewVaga({...newVaga, titulo: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1 uppercase">Preço (R$)</label>
                        <input 
                          type="number" 
                          className="w-full text-sm border rounded p-2"
                          value={newVaga.preco}
                          onChange={e => setNewVaga({...newVaga, preco: Number(e.target.value)})}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-gray-500 mb-1 uppercase">Qtd. Total</label>
                        <input 
                          type="number" 
                          className="w-full text-sm border rounded p-2"
                          value={newVaga.quantidade_total}
                          onChange={e => setNewVaga({...newVaga, quantidade_total: Number(e.target.value)})}
                          required
                        />
                      </div>
                      <button type="submit" className="bg-indigo-600 text-white text-sm font-bold py-2 rounded-lg hover:bg-indigo-700">
                        Adicionar Vaga
                      </button>
                    </form>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Users className="mr-2 h-5 w-5 text-indigo-600" /> Gerenciar Usuários
          </h2>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Admin</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ativo</th>
                  <th scope="col" className="relative px-6 py-3"><span className="sr-only">Ações</span></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.nome_completo || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button 
                        onClick={() => handleToggleSuperuser(user.id, user.is_superuser)}
                        className={`p-1 rounded-full ${user.is_superuser ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                        title={user.is_superuser ? "Remover Admin" : "Tornar Admin"}
                      >
                        {user.is_superuser ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button 
                        onClick={() => handleToggleActive(user.id, user.is_active)}
                        className={`p-1 rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                        title={user.is_active ? "Desativar Usuário" : "Ativar Usuário"}
                      >
                        {user.is_active ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-900 ml-4"
                        title="Excluir Usuário"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};