import React, { useState } from 'react';
import { X, Plus, Trash2, Book, Users, Calendar, DollarSign, Loader2, Info, Check } from 'lucide-react';
import api from '../services/api';
import { useNotification } from '../context/NotificationContext';

interface CreatePublicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  currentUserId: string | null;
}

interface TempVaga {
  titulo: string;
  descricao: string;
  preco: number;
  quantidade_total: number;
  data_encerramento: string;
  pre_requisitos: string;
  imagem_url: string;
}

export const CreatePublicationModal: React.FC<CreatePublicationModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  currentUserId,
}) => {
  const { showNotification } = useNotification();
  const [activeTab, setActiveTab] = useState<'details' | 'vagas'>('details');
  const [loading, setLoading] = useState(false);

  // Publication State
  const [pubData, setPubData] = useState({
    titulo: '',
    subtitulo: '',
    descricao: '',
    tipo: 'livro',
    ano_publicacao: new Date().getFullYear(),
    issn_isbn: '',
    resumo: '',
    area_conhecimento: '',
    data_prevista_publicacao: '',
    tem_doi: false,
    tem_isbn: false,
    tem_issn: false,
  });

  // Temporary Vacancies State (list of vacancies to create)
  const [vagasList, setVagasList] = useState<TempVaga[]>([]);

  // Current vacancy input fields
  const [vagaInput, setVagaInput] = useState<TempVaga>({
    titulo: '',
    descricao: '',
    preco: 0,
    quantidade_total: 1,
    data_encerramento: '',
    pre_requisitos: '',
    imagem_url: '',
  });

  if (!isOpen) return null;

  const resetForm = () => {
    setPubData({
      titulo: '',
      subtitulo: '',
      descricao: '',
      tipo: 'livro',
      ano_publicacao: new Date().getFullYear(),
      issn_isbn: '',
      resumo: '',
      area_conhecimento: '',
      data_prevista_publicacao: '',
      tem_doi: false,
      tem_isbn: false,
      tem_issn: false,
    });
    setVagasList([]);
    setVagaInput({
      titulo: '',
      descricao: '',
      preco: 0,
      quantidade_total: 1,
      data_encerramento: '',
      pre_requisitos: '',
      imagem_url: '',
    });
    setActiveTab('details');
  };

  const handleAddVagaToList = () => {
    if (!vagaInput.titulo.trim()) {
      showNotification('O título da vaga é obrigatório.', 'info');
      return;
    }
    if (vagaInput.preco < 0) {
      showNotification('O preço não pode ser negativo.', 'info');
      return;
    }
    if (vagaInput.quantidade_total < 1) {
      showNotification('A quantidade de vagas deve ser no mínimo 1.', 'info');
      return;
    }

    setVagasList([...vagasList, { ...vagaInput }]);
    // Reset vaga inputs
    setVagaInput({
      titulo: '',
      descricao: '',
      preco: 0,
      quantidade_total: 1,
      data_encerramento: '',
      pre_requisitos: '',
      imagem_url: '',
    });
    showNotification('Vaga adicionada à lista temporária!', 'success');
  };

  const handleRemoveVagaFromList = (index: number) => {
    setVagasList(vagasList.filter((_, i) => i !== index));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!pubData.titulo.trim()) {
      showNotification('O título da publicação é obrigatório.', 'error');
      return;
    }

    setLoading(true);

    try {
      // Prepare publication payload
      const pubPayload = {
        ...pubData,
        ano_publicacao: pubData.ano_publicacao ? Number(pubData.ano_publicacao) : null,
        data_prevista_publicacao: pubData.data_prevista_publicacao || null,
        subtitulo: pubData.subtitulo || null,
        descricao: pubData.descricao || null,
        issn_isbn: pubData.issn_isbn || null,
        resumo: pubData.resumo || null,
        area_conhecimento: pubData.area_conhecimento || null,
      };

      // 1. Create the publication
      const resPub = await api.post('/publications/', pubPayload);
      const pubId = resPub.data.id;

      // 2. Create the associated vacancies
      if (vagasList.length > 0) {
        await Promise.all(
          vagasList.map((vaga) => {
            const vagaPayload = {
              titulo: vaga.titulo,
              descricao: vaga.descricao || null,
              preco: Number(vaga.preco),
              quantidade_total: Number(vaga.quantidade_total),
              data_encerramento: vaga.data_encerramento || null,
              pre_requisitos: vaga.pre_requisitos || null,
              imagem_url: vaga.imagem_url || null,
            };
            return api.post(`/publications/${pubId}/vagas`, vagaPayload);
          })
        );
      }

      showNotification('Publicação e vagas criadas com sucesso!', 'success');
      onSuccess();
      resetForm();
      onClose();
    } catch (error: any) {
      console.error('Erro ao salvar publicação/vagas:', error);
      const msg = error.response?.data?.detail || 'Erro ao registrar os dados.';
      showNotification(`Erro: ${msg}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300"
        onClick={() => !loading && onClose()}
      />

      {/* Modal Container */}
      <div className="relative bg-white rounded-3xl shadow-2xl max-w-4xl w-full overflow-hidden border border-gray-100 flex flex-col max-h-[90vh] transition-all duration-300 transform scale-100">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-100 p-2 rounded-xl text-indigo-600">
              <Book className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-gray-900">Nova Publicação & Coautorias</h2>
              <p className="text-xs text-gray-500">Crie uma obra literária ou científica e defina suas vagas.</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            disabled={loading}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-100 bg-white px-6 flex space-x-6">
          <button
            onClick={() => setActiveTab('details')}
            className={`py-4 px-1 border-b-2 font-bold text-sm flex items-center space-x-2 transition-all ${
              activeTab === 'details'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Book className="h-4 w-4" />
            <span>1. Detalhes da Obra</span>
          </button>
          <button
            onClick={() => setActiveTab('vagas')}
            className={`py-4 px-1 border-b-2 font-bold text-sm flex items-center space-x-2 transition-all ${
              activeTab === 'vagas'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="h-4 w-4" />
            <span>2. Vagas de Coautoria ({vagasList.length})</span>
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Row 1: Title and Subtitle */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Título da Publicação *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ex: Tratado de Direito Constitucional Contemporâneo"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.titulo}
                    onChange={(e) => setPubData({ ...pubData, titulo: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Subtítulo (Opcional)</label>
                  <input
                    type="text"
                    placeholder="Ex: Teoria e Prática nos Tribunais"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.subtitulo}
                    onChange={(e) => setPubData({ ...pubData, subtitulo: e.target.value })}
                  />
                </div>
              </div>

              {/* Row 2: Type, Area and Year */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Tipo de Obra</label>
                  <select
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm font-medium"
                    value={pubData.tipo}
                    onChange={(e) => setPubData({ ...pubData, tipo: e.target.value })}
                  >
                    <option value="livro">Livro</option>
                    <option value="artigo">Artigo</option>
                    <option value="capitulo">Capítulo de Livro</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Área de Conhecimento</label>
                  <input
                    type="text"
                    placeholder="Ex: Ciências Jurídicas, Saúde"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.area_conhecimento}
                    onChange={(e) => setPubData({ ...pubData, area_conhecimento: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Ano da Publicação</label>
                  <input
                    type="number"
                    placeholder="Ex: 2026"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.ano_publicacao}
                    onChange={(e) => setPubData({ ...pubData, ano_publicacao: Number(e.target.value) })}
                  />
                </div>
              </div>

              {/* Row 3: Expected Date and ISSN/ISBN */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Previsão de Lançamento</label>
                  <input
                    type="date"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.data_prevista_publicacao}
                    onChange={(e) => setPubData({ ...pubData, data_prevista_publicacao: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Código ISBN / ISSN (Opcional)</label>
                  <input
                    type="text"
                    placeholder="Ex: 978-3-16-148410-0"
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
                    value={pubData.issn_isbn}
                    onChange={(e) => setPubData({ ...pubData, issn_isbn: e.target.value })}
                  />
                </div>
              </div>

              {/* Row 4: Identifiers switches */}
              <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                <span className="block text-xs font-extrabold text-gray-500 uppercase tracking-wider mb-3">Atributos e Indexadores</span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white border border-gray-200 rounded-xl hover:border-indigo-200 transition-colors select-none">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer"
                      checked={pubData.tem_doi}
                      onChange={(e) => setPubData({ ...pubData, tem_doi: e.target.checked })}
                    />
                    <div>
                      <span className="block text-sm font-bold text-gray-900">DOI Indexado</span>
                      <span className="text-[10px] text-gray-500">Obra possuirá prefixo DOI.</span>
                    </div>
                  </label>

                  <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white border border-gray-200 rounded-xl hover:border-indigo-200 transition-colors select-none">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer"
                      checked={pubData.tem_isbn}
                      onChange={(e) => setPubData({ ...pubData, tem_isbn: e.target.checked })}
                    />
                    <div>
                      <span className="block text-sm font-bold text-gray-900">ISBN Vinculado</span>
                      <span className="text-[10px] text-gray-500">Registro para formato livro.</span>
                    </div>
                  </label>

                  <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white border border-gray-200 rounded-xl hover:border-indigo-200 transition-colors select-none">
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer"
                      checked={pubData.tem_issn}
                      onChange={(e) => setPubData({ ...pubData, tem_issn: e.target.checked })}
                    />
                    <div>
                      <span className="block text-sm font-bold text-gray-900">ISSN Vinculado</span>
                      <span className="text-[10px] text-gray-500">Registro para periódico.</span>
                    </div>
                  </label>
                </div>
              </div>

              {/* Description & Summary */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Resumo / Abstract</label>
                  <textarea
                    rows={4}
                    placeholder="Insira um resumo breve da proposta científica ou acadêmica..."
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm resize-none"
                    value={pubData.resumo}
                    onChange={(e) => setPubData({ ...pubData, resumo: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1">Descrição Detalhada</label>
                  <textarea
                    rows={4}
                    placeholder="Descrição para controle editorial interna ou notas de organização..."
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm resize-none"
                    value={pubData.descricao}
                    onChange={(e) => setPubData({ ...pubData, descricao: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'vagas' && (
            <div className="space-y-6">
              {/* Form to add a vacancy */}
              <div className="bg-indigo-50/50 p-6 rounded-2xl border border-indigo-100/50">
                <h3 className="text-sm font-extrabold text-indigo-900 mb-4 flex items-center">
                  <Plus className="h-4 w-4 mr-2" /> Preencher Nova Vaga
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">Título da Vaga *</label>
                    <input
                      type="text"
                      placeholder="Ex: Coautor - Revisão de Literatura"
                      className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                      value={vagaInput.titulo}
                      onChange={(e) => setVagaInput({ ...vagaInput, titulo: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">Preço Unitário (R$) *</label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <DollarSign className="h-3.5 w-3.5 text-gray-400" />
                      </div>
                      <input
                        type="number"
                        placeholder="1500"
                        className="w-full pl-8 pr-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                        value={vagaInput.preco}
                        onChange={(e) => setVagaInput({ ...vagaInput, preco: Number(e.target.value) })}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">Quantidade de Vagas *</label>
                    <input
                      type="number"
                      min={1}
                      placeholder="1"
                      className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                      value={vagaInput.quantidade_total}
                      onChange={(e) => setVagaInput({ ...vagaInput, quantidade_total: Number(e.target.value) })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">Pré-requisitos do Coautor</label>
                    <input
                      type="text"
                      placeholder="Ex: Mestrado em andamento ou superior"
                      className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                      value={vagaInput.pre_requisitos}
                      onChange={(e) => setVagaInput({ ...vagaInput, pre_requisitos: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">Data Limite de Inscrição</label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Calendar className="h-3.5 w-3.5 text-gray-400" />
                      </div>
                      <input
                        type="date"
                        className="w-full pl-8 pr-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                        value={vagaInput.data_encerramento}
                        onChange={(e) => setVagaInput({ ...vagaInput, data_encerramento: e.target.value })}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">URL da Imagem da Vaga</label>
                    <input
                      type="url"
                      placeholder="https://exemplo.com/capas/imagem.png"
                      className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs"
                      value={vagaInput.imagem_url}
                      onChange={(e) => setVagaInput({ ...vagaInput, imagem_url: e.target.value })}
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-xs font-bold text-gray-600 mb-1">Descrição / Escopo da Vaga</label>
                  <textarea
                    rows={2}
                    placeholder="Descrição breve do trabalho que o coautor irá desempenhar..."
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-xs resize-none"
                    value={vagaInput.descricao}
                    onChange={(e) => setVagaInput({ ...vagaInput, descricao: e.target.value })}
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={handleAddVagaToList}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-xl font-bold text-xs hover:bg-indigo-700 transition-colors flex items-center space-x-1 shadow-sm"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    <span>Adicionar Vaga à Obra</span>
                  </button>
                </div>
              </div>

              {/* Temp list display */}
              <div className="space-y-3">
                <span className="block text-xs font-extrabold text-gray-500 uppercase tracking-wider">Lista de Vagas Cadastradas nesta Publicação ({vagasList.length})</span>
                {vagasList.length === 0 ? (
                  <div className="text-center py-8 border border-dashed border-gray-200 rounded-2xl bg-gray-50/50">
                    <Info className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 font-medium">Nenhuma vaga adicionada ainda.</p>
                    <p className="text-xs text-gray-400">Você pode adicionar vagas acima ou criá-las depois no painel.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {vagasList.map((vaga, index) => (
                      <div 
                        key={index} 
                        className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex items-start justify-between hover:border-indigo-200 transition-colors"
                      >
                        <div className="space-y-1.5 flex-1 pr-4">
                          <div className="flex items-center space-x-2">
                            <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded-md">
                              {vaga.quantidade_total}x {vaga.quantidade_total === 1 ? 'Vaga' : 'Vagas'}
                            </span>
                            <span className="text-green-600 text-xs font-bold">R$ {vaga.preco.toFixed(2)}</span>
                          </div>
                          <h4 className="font-extrabold text-sm text-gray-900">{vaga.titulo}</h4>
                          {vaga.pre_requisitos && (
                            <p className="text-xs text-gray-500"><strong className="text-gray-700">Req:</strong> {vaga.pre_requisitos}</p>
                          )}
                          {vaga.data_encerramento && (
                            <p className="text-[10px] text-amber-600 font-medium">Adesão até: {new Date(vaga.data_encerramento).toLocaleDateString('pt-BR')}</p>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveVagaFromList(index)}
                          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                          title="Remover vaga"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50 flex justify-between items-center">
          <div className="text-xs text-gray-500 font-medium">
            {activeTab === 'details' ? (
              <span>Passo 1 de 2: Defina as propriedades básicas da obra.</span>
            ) : (
              <span>Passo 2 de 2: Defina e liste as vagas.</span>
            )}
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              disabled={loading}
              onClick={onClose}
              className="px-5 py-2.5 border border-gray-200 rounded-xl font-bold text-sm text-gray-700 bg-white hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            {activeTab === 'details' ? (
              <button
                type="button"
                onClick={() => setActiveTab('vagas')}
                className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-bold text-sm hover:bg-indigo-700 transition-colors shadow-sm"
              >
                Avançar: Vagas de Coautoria
              </button>
            ) : (
              <button
                type="button"
                disabled={loading}
                onClick={handleSave}
                className="px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl font-bold text-sm transition-colors shadow-sm flex items-center space-x-1.5"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Salvando tudo...</span>
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Salvar Publicação & Vagas</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
