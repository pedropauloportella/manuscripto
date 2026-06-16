import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Users, ShieldCheck, ArrowRight } from 'lucide-react';

export const Home = () => {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative py-24 overflow-hidden bg-gradient-to-br from-indigo-950 via-indigo-900 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
              A Revolução na Gestão <span className="text-indigo-400">Editorial Acadêmica</span>
            </h1>
            <p className="text-xl text-indigo-100 max-w-2xl mx-auto mb-10">
              Do manuscrito à distribuição. Uma plataforma completa para autores, editores e pesquisadores 
              facilitarem o fluxo de coautoria e publicações científicas.
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link to="/catalog" className="px-8 py-3 bg-indigo-500 hover:bg-indigo-400 text-white font-bold rounded-lg transition-colors flex items-center">
                Explorar Catálogo <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link to="/login" className="px-8 py-3 bg-white text-indigo-900 font-bold rounded-lg hover:bg-gray-100 transition-colors">
                Começar Agora
              </Link>
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-indigo-500 rounded-full blur-3xl opacity-20"></div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group">
              <div className="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BookOpen className="h-8 w-8" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Gestão Completa</h3>
              <p className="text-gray-600">Controle todas as etapas: submissão, revisão por pares, versionamento e publicação final.</p>
            </div>
            
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group">
              <div className="w-16 h-16 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Users className="h-8 w-8" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Coautoria Simplificada</h3>
              <p className="text-gray-600">Sistema transparente de aquisição de vagas de coautoria com vinculação automática via MercadoPago.</p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group">
              <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ShieldCheck className="h-8 w-8" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Segurança e Ética</h3>
              <p className="text-gray-600">Autenticação via ORCID e Google, garantindo a integridade dos perfis acadêmicos.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Pronto para publicar sua próxima obra?</h2>
          <p className="text-lg text-gray-600 mb-8">Junte-se a centenas de pesquisadores que já estão utilizando o Manuscripto para acelerar suas publicações acadêmicas.</p>
          <Link to="/login" className="text-indigo-600 font-bold hover:text-indigo-500 underline underline-offset-4">
            Crie sua conta agora gratuitamente
          </Link>
        </div>
      </section>
    </div>
  );
};