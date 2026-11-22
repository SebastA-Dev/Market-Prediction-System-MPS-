/**
 * Entidad de Dominio: User
 * Representa al usuario de la plataforma y su sesión autenticada.
 */
export class User {
  constructor({ id = null, email = '', displayName = 'Invitado', riskProfile = '', createdAt = null, token = null }) {
    this.id = id;
    this.email = email;
    this.displayName = displayName;
    this.riskProfile = riskProfile;
    this.createdAt = createdAt;
    this.token = token;
  }

  get initials() {
    if (!this.displayName) return 'IN';
    const parts = this.displayName.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  get isAuthenticated() {
    return Boolean(this.token && this.id);
  }
}
