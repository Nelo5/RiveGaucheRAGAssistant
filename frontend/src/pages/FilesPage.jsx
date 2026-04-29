import { useState, useEffect } from 'react';
import { api } from '../api';

export default function FilesPage() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadFiles = async () => {
    try {
      const data = await api.getFiles();
      setFiles(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await api.uploadFile(file);
      await loadFiles();
    } catch (err) {
      setError(`Ошибка загрузки: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Удалить файл?')) return;
    try {
      await api.deleteFile(fileId);
      await loadFiles();
    } catch (err) {
      setError(`Ошибка удаления: ${err.message}`);
    }
  };

  return (
    <div className="files-page">
      <h2>Управление файлами</h2>
      {error && <p className="error">{error}</p>}
      <div className="upload-section">
        <input type="file" onChange={handleUpload} disabled={uploading} />
        {uploading && <span>Загрузка...</span>}
      </div>
      <table className="files-table">
        <thead>
          <tr>
            <th>ID файла</th>
            <th>Имя</th>
            <th>Загружен</th>
            <th>Чанки</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.file_id}>
              <td>{file.file_id}</td>
              <td>{file.filename}</td>
              <td>{new Date(file.uploaded_at).toLocaleString()}</td>
              <td>{file.chunks}</td>
              <td>
                <button className="btn btn-danger" onClick={() => handleDelete(file.file_id)}>
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}