#  AnalizaPerú — Sistema de Análisis de Noticias Peruanas con PLN

**Proyecto PC3 · Procesamiento de Lenguaje Natural 2026**

Aplicación que recolecta, procesa y analiza noticias peruanas de RPP Noticias y Diario Líbero usando técnicas de PLN: clasificación de texto, análisis de sentimiento y reconocimiento de entidades (NER).

---

## Técnicas PLN aplicadas

1. **Preprocesamiento**: limpieza, tokenización, stopwords en español, lematización por reglas
2. **Clasificación de texto**: clasificador por diccionario de keywords (Política, Deportes, Economía, Seguridad, Clima)
3. **Análisis de sentimiento**: léxico de polaridad positiva/negativa con score continuo
4. **NER**: gazeteer de entidades del contexto peruano (personas, organizaciones, lugares)

---



## Fuentes de datos

- **RPP Noticias** — [rpp.pe](https://rpp.pe) (Política, Economía, Actualidad)
- **Diario Líbero** — [libero.pe](https://libero.pe) (Deportes)

Las noticias usadas corresponden a eventos reales del 22-24 de mayo de 2026.
