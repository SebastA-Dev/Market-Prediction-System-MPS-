/**
 * Entidad de Dominio: EducationalTerm
 * Representa un concepto, métrica, tipo de activo o recurso pedagógico en el Hub Educativo (UC-08, RF-41).
 */
export class EducationalTerm {
  constructor({
    id,
    title,
    category, // 'metricas' | 'activos' | 'youtube' | 'herramientas'
    badge,
    badgeColor = 'emerald',
    description,
    formula = null,
    whyIaUses = null,
    example = null,
    externalUrl = null,
    channel = null,
    duration = null,
    topics = null,
    keywords = []
  }) {
    this.id = id;
    this.title = title;
    this.category = category;
    this.badge = badge;
    this.badgeColor = badgeColor;
    this.description = description;
    this.formula = formula;
    this.whyIaUses = whyIaUses;
    this.example = example;
    this.externalUrl = externalUrl;
    this.channel = channel;
    this.duration = duration;
    this.topics = topics;
    this.keywords = keywords;
  }
}
