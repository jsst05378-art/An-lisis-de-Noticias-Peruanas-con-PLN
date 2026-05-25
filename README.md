# 📰 AnalizaPerú — Sistema de Análisis de Noticias Peruanas con PLN

**Proyecto PC3 · Procesamiento de Lenguaje Natural 2026**

Aplicación que recolecta, procesa y analiza noticias peruanas de RPP Noticias y Diario Líbero usando técnicas de PLN: clasificación de texto, análisis de sentimiento y reconocimiento de entidades (NER).

---

## Técnicas PLN aplicadas

1. **Preprocesamiento**: limpieza, tokenización, stopwords en español, lematización por reglas
2. **Clasificación de texto**: clasificador por diccionario de keywords (Política, Deportes, Economía, Seguridad, Clima)
3. **Análisis de sentimiento**: léxico de polaridad positiva/negativa con score continuo
4. **NER**: gazeteer de entidades del contexto peruano (personas, organizaciones, lugares)

---

## Correr localmente

### Paso 1 — Clonar o descomprimir el proyecto

```bash
cd proyecto_nlp_noticias
```

### Paso 2 — Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4 — Ejecutar la app

```bash
streamlit run app.py
```

Abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## Desplegar en Streamlit Cloud (gratis)

### Paso 1 — Subir el código a GitHub

1. Crea un repositorio nuevo en [github.com](https://github.com) (puede ser privado)
2. Sube estos archivos:
   ```
   app.py
   requirements.txt
   README.md
   ```

   Puedes hacerlo con:
   ```bash
   git init
   git add app.py requirements.txt README.md
   git commit -m "Proyecto PC3 - NLP Noticias Peruanas"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

### Paso 2 — Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona:
   - **Repository**: tu repositorio recién creado
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Haz clic en **"Deploy!"**
6. En 2-3 minutos tendrás una URL pública tipo:
   `https://tu-usuario-proyecto-nlp-noticias-app-XXXXX.streamlit.app`

---

## Estructura del proyecto

```
proyecto_nlp_noticias/
├── app.py                        # Aplicación Streamlit principal
├── requirements.txt              # Dependencias Python
├── notebook_nlp_noticias.ipynb   # Notebook documentado para entregar
└── README.md                     # Este archivo
```

---

## Entregables del proyecto

| Entregable | Archivo |
|---|---|
| Código fuente | `app.py` |
| Notebook documentado | `notebook_nlp_noticias.ipynb` |
| App Streamlit (local) | `streamlit run app.py` |
| App Streamlit (nube) | URL de Streamlit Cloud |
| Repositorio GitHub | Subir todo el proyecto |

---

## Fuentes de datos

- **RPP Noticias** — [rpp.pe](https://rpp.pe) (Política, Economía, Actualidad)
- **Diario Líbero** — [libero.pe](https://libero.pe) (Deportes)

Las noticias usadas corresponden a eventos reales del 22-24 de mayo de 2026.
