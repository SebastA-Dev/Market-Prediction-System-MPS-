import { IStoragePort } from '../../../domain/ports/out/INotificationAndStoragePorts.js';

/**
 * Adaptador de Salida: BrowserStorageAdapter
 * Implementa IStoragePort utilizando localStorage del navegador de forma segura.
 */
export class BrowserStorageAdapter extends IStoragePort {
  getItem(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      console.warn('No se pudo leer de localStorage:', e);
      return null;
    }
  }

  setItem(key, value) {
    try {
      localStorage.setItem(key, String(value));
    } catch (e) {
      console.warn('No se pudo escribir en localStorage:', e);
    }
  }

  removeItem(key) {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.warn('No se pudo eliminar de localStorage:', e);
    }
  }
}
