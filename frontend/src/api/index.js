const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://rksp-kursach-ba-latest.onrender.com';

async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    ...options.headers,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  // Для FormData не устанавливаем Content-Type, браузер сам добавит boundary
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(`${BASE_URL}${url}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail?.[0]?.msg || 'Request failed');
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  // Авторизация
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email, password) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getUserInfo: (token) =>
    request('/auth/me', {
      method: 'GET',
    }),

  // Чат
  getChats: () => request('/chats'),
  createChat: () =>
    request('/chats', {
      method: 'POST',
    }),
  getMessages: (chatId) => request(`/chats/${chatId}/messages`),
  sendMessage: (chatId, content) =>
    request(`/chats/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  // Публичный запрос
  query: (question) =>
    request('/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),

  // Файлы (только для админа)
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/files/upload', {
      method: 'POST',
      body: formData,
    });
  },
  getFiles: () => request('/files'),
  getFile: (fileId) => request(`/files/${fileId}`),
  deleteFile: (fileId) =>
    request(`/files/${fileId}`, {
      method: 'DELETE',
    }),
};