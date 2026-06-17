import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Check, ShieldAlert, Activity, X } from 'lucide-react';

interface Notification {
  message: string;
  type: 'success' | 'error' | 'info';
}

interface NotificationContextType {
  showNotification: (message: string, type?: 'success' | 'error' | 'info') => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notification, setNotification] = useState<Notification | null>(null);

  const showNotification = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(prev => (prev?.message === message ? null : prev));
    }, 5000);
  }, []);

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-xl border-l-4 flex items-center justify-between min-w-[300px] animate-in slide-in-from-right duration-300 ${
          notification.type === 'success' ? 'bg-green-50 border-green-500 text-green-800' :
          notification.type === 'error' ? 'bg-red-50 border-red-500 text-red-800' :
          'bg-blue-50 border-blue-500 text-blue-800'
        }`}>
          <div className="flex items-center">
            {notification.type === 'success' && <Check className="h-5 w-5 mr-2" />}
            {notification.type === 'error' && <ShieldAlert className="h-5 w-5 mr-2" />}
            {notification.type === 'info' && <Activity className="h-5 w-5 mr-2" />}
            <span className="font-medium">{notification.message}</span>
          </div>
          <button onClick={() => setNotification(null)} className="ml-4 text-gray-400 hover:text-gray-600">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};