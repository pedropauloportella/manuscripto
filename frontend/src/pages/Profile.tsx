import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { supabase } from '../services/supabase';
import api from '../services/api';
import { useNotification } from '../context/NotificationContext';
import { User, Mail, MapPin, School, GraduationCap, Link as LinkIcon, Save, Loader2, Linkedin, Instagram, ExternalLink } from 'lucide-react';

export const Profile = () => {
  const { id } = useParams<{ id: string }>();
  const [userData, setUserData] = useState<any>(null);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { showNotification } = useNotification();

  const isOwner = currentUserId === id;

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Obtém o usuário logado para comparar com o ID da URL
        const { data: { session } } = await supabase.auth.getSession();
        setCurrentUserId(session?.user?.id || null);

        // Busca os dados do perfil pelo ID do slug
        const res = await api.get(`/auth/profile/${id}`);
        setUserData(res.data);
      } catch (error) {
        showNotification("Erro ao carregar perfil", "error");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchProfile();
  }, [id, showNotification]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put('/auth/me', userData);
      showNotification("Perfil atualizado com sucesso!", "success");
    } catch (error) {
      showNotification("Erro ao atualizar perfil", "error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-[60vh]"><Loader2 className="animate-spin h-10 w-10 text-indigo-600" /></div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="bg-indigo-600 h-32"></div>
        <div className="px-8 pb-8">
          <div className="relative -mt-16 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div className="p-1 bg-white rounded-2xl">
              <img 
                src={userData.avatar_url || `https://ui-avatars.com/api/?name=${userData.nome_completo || 'User'}&background=random`} 
                alt="Avatar" 
                className="h-32 w-32 rounded-xl object-cover border-4 border-white shadow-md"
              />
            </div>
            {!isOwner && (
              <div className="mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{userData.nome_completo}</h1>
                <p className="text-gray-500 flex items-center">
                  <GraduationCap className="h-4 w-4 mr-1" /> {userData.grau_formacao || 'Pesquisador'}
                </p>
              </div>
            )}
          </div>

          <form onSubmit={handleSave} className="space-y-8">
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <User className="h-5 w-5 mr-2 text-indigo-600" /> 
                {isOwner ? "Minhas Informações" : "Informações do Autor"}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nome Completo</label>
                  <input 
                    type="text" 
                    disabled={!isOwner}
                    className="w-full p-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                    value={userData.nome_completo || ''}
                    onChange={e => setUserData({...userData, nome_completo: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <input 
                      type="text" 
                      disabled={!isOwner}
                      className="w-full pl-10 pr-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Ex: São Paulo, SP"
                      value={userData.cidade || ''}
                      onChange={e => setUserData({...userData, cidade: e.target.value})}
                    />
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <School className="h-5 w-5 mr-2 text-indigo-600" /> Acadêmico
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Universidade / Instituição</label>
                  <input 
                    type="text" 
                    disabled={!isOwner}
                    className="w-full p-2 border rounded-lg"
                    value={userData.universidade || ''}
                    onChange={e => setUserData({...userData, universidade: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Área de Formação</label>
                  <input 
                    type="text" 
                    disabled={!isOwner}
                    className="w-full p-2 border rounded-lg"
                    value={userData.area_formacao || ''}
                    onChange={e => setUserData({...userData, area_formacao: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Grau de Formação</label>
                  <select 
                    disabled={!isOwner}
                    className="w-full p-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                    value={userData.grau_formacao || ''}
                    onChange={e => setUserData({...userData, grau_formacao: e.target.value})}
                  >
                    <option value="">Selecione...</option>
                    <option value="Graduando">Graduando</option>
                    <option value="Graduado">Graduado</option>
                    <option value="Mestrando">Mestrando</option>
                    <option value="Mestre">Mestre</option>
                    <option value="Doutorando">Doutorando</option>
                    <option value="Doutorado">Doutorado</option>
                  </select>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <LinkIcon className="h-5 w-5 mr-2 text-indigo-600" /> Links e Redes Sociais
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="relative">
                    <ExternalLink className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <input disabled={!isOwner} className="w-full pl-10 pr-3 py-2 border rounded-lg disabled:bg-gray-50" placeholder="URL do Lattes" value={userData.lattes_link || ''} onChange={e => setUserData({...userData, lattes_link: e.target.value})} />
                    {!isOwner && userData.lattes_link && (
                      <a href={userData.lattes_link} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 mt-1 block hover:underline">Acessar Lattes</a>
                    )}
                  </div>
                  <div className="relative">
                    <img src="https://orcid.org/assets/vectors/orcid.logo.icon.svg" className="absolute left-3 top-2.5 h-4 w-4" alt="ORCID" />
                    <input disabled={!isOwner} className="w-full pl-10 pr-3 py-2 border rounded-lg disabled:bg-gray-50" placeholder="ID ORCID" value={userData.orcid_id || ''} onChange={e => setUserData({...userData, orcid_id: e.target.value})} />
                    {userData.orcid_id && (
                      <a href={`https://orcid.org/${userData.orcid_id}`} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 mt-1 block hover:underline">Ver no ORCID</a>
                    )}
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="relative">
                    <Linkedin className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <input disabled={!isOwner} className="w-full pl-10 pr-3 py-2 border rounded-lg disabled:bg-gray-50" placeholder="URL Linkedin" value={userData.linkedin_link || ''} onChange={e => setUserData({...userData, linkedin_link: e.target.value})} />
                    {!isOwner && userData.linkedin_link && (
                      <a href={userData.linkedin_link} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 mt-1 block hover:underline">Ver LinkedIn</a>
                    )}
                  </div>
                  <div className="relative">
                    <Instagram className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <input disabled={!isOwner} className="w-full pl-10 pr-3 py-2 border rounded-lg disabled:bg-gray-50" placeholder="URL Instagram" value={userData.instagram_link || ''} onChange={e => setUserData({...userData, instagram_link: e.target.value})} />
                    {!isOwner && userData.instagram_link && (
                      <a href={userData.instagram_link} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 mt-1 block hover:underline">Ver Instagram</a>
                    )}
                  </div>
                </div>
              </div>
            </section>

            {isOwner && (
              <div className="flex justify-end pt-6">
                <button 
                  type="submit" 
                  disabled={saving}
                  className="flex items-center px-6 py-2 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {saving ? <Loader2 className="animate-spin h-5 w-5 mr-2" /> : <Save className="h-5 w-5 mr-2" />}
                  Salvar Alterações
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};