# Automatización de Posts en LinkedIn con IA e Interfaz Web (Streamlit)

Este proyecto proporciona una herramienta con una interfaz web interactiva, creada con Streamlit, para automatizar la creación y publicación de posts en LinkedIn. Utiliza inteligencia artificial y diversas APIs para ofrecer un flujo de trabajo completo:

* **Descubrimiento de Temas (¡Nuevo!)**: Sugiere noticias y temas de actualidad relacionados con la Inteligencia Artificial utilizando la **API de NewsAPI**, permitiendo al usuario encontrar inspiración antes de generar el contenido.
* **Búsqueda de Información**: Obtiene información relevante y actual sobre un tema específico usando la API de Google Custom Search.
* **Generación de Contenido de Texto**: Redacta el contenido del post con la API de OpenAI (modelos como GPT-4o), basándose en el tema y la información recopilada.
* **Generación de Imágenes**: Crea imágenes originales y temáticas para el post mediante la API DALL-E de OpenAI.
* **Limpieza, Previsualización y Edición**: Normaliza el texto generado y permite al usuario previsualizar el post completo (texto e imagen) y editar el texto directamente en la interfaz.
* **Publicación en LinkedIn**: Sube la imagen y publica el contenido final en el perfil del usuario a través de la API de LinkedIn (endpoints `/rest/images` y `/rest/posts`).

## Requisitos Previos

* Python 3.8 o superior.
* Git (para clonar el repositorio).
* Una cuenta de desarrollador en [OpenAI Platform](https://platform.openai.com/).
* Una cuenta en [NewsAPI](https://newsapi.org) para obtener noticias.
* Una cuenta de [Google Cloud Platform](https://cloud.google.com/) con la API de Custom Search habilitada.
* Una cuenta de desarrollador en [LinkedIn](https://developer.linkedin.com/).
* Navegador web moderno (Chrome, Firefox, Edge, Safari) para interactuar con la interfaz de Streamlit.

## 🛠️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto:

### 1. Clonar el Repositorio

Abre tu terminal o consola, navega al directorio donde deseas guardar el proyecto y ejecuta:

```bash
git clone [https://github.com/aseinotegi/LinkedinAutomation.git](https://github.com/aseinotegi/LinkedinAutomation.git)
cd LinkedinAutomation

```

### 2\. Crear y Activar un Entorno Virtual

Es altamente recomendable usar un entorno virtual para gestionar las dependencias del proyecto.

-   **Crear el entorno virtual** (si no existe uno llamado `venv`):

    Bash

    ```
    python -m venv venv

    ```

    (En algunos sistemas, puede que necesites usar `python3`).
-   **Activar el entorno virtual:**
    -   En Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
    -   En Windows (Command Prompt): `venv\Scripts\activate`
    -   En macOS y Linux: `source venv/bin/activate`

### 3\. Instalar Dependencias

Con el entorno virtual activado, instala todas las bibliotecas de Python necesarias:

Bash

```
pip install -r requirements.txt

```

### 4\. Configurar Variables de Entorno (Archivo `.env`)

Este proyecto utiliza un archivo `.env` para gestionar las claves de API y otras configuraciones.

-   Crea un archivo llamado `.env` en el directorio raíz del proyecto (al mismo nivel que los archivos `.py`).
-   Añade las siguientes variables a tu archivo `.env`, reemplazando los valores de ejemplo con tus propias credenciales:

<!-- end list -->

Fragmento de código

```
# Credenciales de OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Opcional: Modelos de OpenAI (si no se especifican, se usan los defaults del script)
# OPENAI_MODEL=gpt-4o
# DALLE_MODEL=dall-e-3
# OPENAI_MAX_TOKENS=1500
# OPENAI_TEMPERATURE=0.7

# Credenciales de NewsAPI (¡Nuevo!)
NEWSAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Credenciales de API de búsqueda (Google Custom Search)
SEARCH_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SEARCH_ENGINE_ID=xxxxxxxxxxxxxxxxxxxxxxxxx

# Credenciales de LinkedIn
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxxx
LINKEDIN_USER_URN=urn:li:person:xxxxxxxxxx
# Opcional: Versión de la API de LinkedIn (si no se especifica, se usa el default del script, ej. "202504")
# LINKEDIN_API_VERSION=202504

```

### 5\. Obtención de Credenciales

Si no tienes alguna de las claves API, aquí te indicamos cómo obtenerlas:

-   **OpenAI API Key (`OPENAI_API_KEY`)**:

    -   Regístrate o inicia sesión en [OpenAI Platform](https://platform.openai.com/).
    -   Ve a la sección "API Keys" en tu panel de control.
    -   Crea una nueva clave secreta y cópiala. Asegúrate de tener fondos o créditos en tu cuenta.
-   **NewsAPI Key (`NEWSAPI_KEY`) (¡Nuevo!)**:

    -   Regístrate para obtener una API key en [NewsAPI.org](https://newsapi.org/register).
    -   Una vez registrado, encontrarás tu API key en el dashboard de tu cuenta.
-   **Google Custom Search API (`SEARCH_API_KEY`, `SEARCH_ENGINE_ID`)**:

    -   Ve a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto (o selecciona uno existente).
    -   Habilita la "Custom Search API" para tu proyecto.
    -   En "Credenciales", crea una "Clave de API". Esa será tu `SEARCH_API_KEY`.
    -   Ve a [Google Programmable Search Engine](https://programmablesearchengine.google.com/).
    -   Crea un nuevo motor de búsqueda (puedes configurarlo para buscar en toda la web).
    -   Una vez creado, copia el "ID del motor de búsqueda". Ese será tu `SEARCH_ENGINE_ID`.
-   **LinkedIn API (`LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_USER_URN`)**:

    -   Crea una aplicación en el [Portal de Desarrolladores de LinkedIn](https://www.google.com/search?q=https://developer.linkedin.com/apps).
    -   Completa los detalles de la aplicación (nombre, asocia una página de LinkedIn, logo, etc.).
    -   En la pestaña **"Products"** (Productos) de tu aplicación, solicita y asegúrate de que estén **activos** los siguientes productos:
        -   `Share on LinkedIn` (otorga el permiso `w_member_social` para publicar).
        -   `Sign In with LinkedIn using OpenID Connect` (otorga permisos como `openid` y `profile` para leer tu ID de usuario).
    -   En la pestaña **"Auth"** (Autenticación):
        -   Anota tu `Client ID` y `Client Secret`.
        -   Añade una **URL de redirección autorizada**. Para usar la herramienta de generación de tokens del portal, `https://www.linkedin.com/developers/tools/oauth/redirect` es una buena opción.
    -   **Generar el Token de Acceso (`LINKEDIN_ACCESS_TOKEN`)**:
        -   Usa la herramienta "OAuth 2.0 token generator" en la pestaña "Auth" o "Tools" de tu aplicación en el portal de desarrolladores.
        -   Selecciona los **scopes (permisos)**: `openid`, `profile`, y `w_member_social`.
        -   Copia el token de acceso generado.
    -   **Obtener tu URN de Usuario (`LINKEDIN_USER_URN`)**:
        -   Con el token de acceso (que incluye los permisos `openid` y `profile`), haz una solicitud GET a `https://api.linkedin.com/v2/userinfo`.
        -   La cabecera de autorización debe ser `Authorization: Bearer TU_TOKEN_DE_ACCESO`.
        -   La respuesta JSON contendrá un campo `sub`. Tu URN será `urn:li:person:VALOR_DE_SUB`.

🚀 Ejecutar y Usar la Aplicación (Interfaz Web con Streamlit)
-------------------------------------------------------------

La aplicación se ejecuta como una interfaz web interactiva en tu navegador.

1.  **Activa tu Entorno Virtual**: Asegúrate de que tu entorno virtual (`venv`) esté activado en tu terminal (ver paso 2 de Instalación).
2.  **Navega al Directorio del Proyecto**: En tu terminal, asegúrate de estar en el directorio raíz del proyecto (donde se encuentran los archivos `st_linkedin_app.py` y `linkedin_post_automation.py`).
3.  **Ejecuta el Comando de Streamlit**:

    Bash

    ```
    streamlit run st_linkedin_app.py

    ```

4.  **Abre la Aplicación en tu Navegador**: Streamlit iniciará un servidor local y, por lo general, abrirá automáticamente una nueva pestaña en tu navegador web con la aplicación. Si no lo hace, la terminal te mostrará las URLs (Local y Network) donde puedes acceder a ella (normalmente `http://localhost:8501`).

### Uso de la Interfaz:

-   **Paso Opcional: Descubrir Temas (Sidebar)**

    -   En la barra lateral izquierda, encontrarás la sección "💡 Descubrir Temas".
    -   Haz clic en el botón "Buscar Noticias de IA (Global)".
    -   El sistema consultará NewsAPI y mostrará una lista de titulares de noticias recientes relacionadas con la IA.
    -   Puedes hacer clic en cualquiera de estos titulares sugeridos para que se rellene automáticamente el campo de tema principal.
-   **Paso 1: Define el Tema del Post**

    -   Ingresa el tema sobre el cual quieres generar el post en el campo de texto "Ingresa el tema para tu post de LinkedIn:". Si seleccionaste un tema de la barra lateral, este campo ya estará relleno, pero puedes editarlo.
-   **Paso 2: Genera Contenido y Vista Previa**

    -   Haz clic en el botón "✨ Generar Contenido y Vista Previa".
    -   El sistema realizará la búsqueda de información contextual (Google Search), la generación de texto (OpenAI GPT), la limpieza del texto y la generación de una imagen (OpenAI DALL-E). Esto puede tardar unos momentos.
-   **Paso 3: Revisa y Edita**

    -   El texto del post generado por la IA aparecerá en un área de texto. **Puedes editar este texto directamente en la interfaz** para ajustarlo a tu gusto.
    -   Se mostrará la imagen generada por DALL-E.
-   **Paso 4: Confirma y Publica**

    -   Cuando estés satisfecho con el texto editado y la imagen, haz clic en el botón "🚀 Publicar en LinkedIn".
-   **Resultado**: La aplicación te informará si la publicación fue exitosa y te mostrará el ID del post creado en LinkedIn.

⚠️ Limitaciones y Consideraciones
---------------------------------

-   **Costos de API**: El uso de las APIs de OpenAI (GPT y DALL-E) y NewsAPI (dependiendo del plan y uso) puede tener costos asociados.
-   **Validez del Token de LinkedIn**: Los tokens de acceso de LinkedIn expiran (aprox. 60 días). Necesitarás generar uno nuevo cuando esto ocurra.
-   **Límites de Tasa de API**: Todas las APIs tienen límites de uso. Revisa la documentación de cada API para más detalles.
-   **Calidad de las Noticias**: La relevancia y calidad de las noticias de NewsAPI pueden variar. La selección de temas puede requerir criterio.
-   **Políticas de Contenido**: El contenido debe cumplir con las políticas de OpenAI y LinkedIn.
-   **Conexión a Internet**: Se requiere una conexión a internet activa.

🔧 Solución de Problemas
------------------------

-   **Error de Variables de Entorno**: Verifica tu archivo `.env` (ubicación correcta en la raíz del proyecto, nombres exactos de las variables, valores correctos sin espacios extra).
-   **Error de Autenticación en LinkedIn (401/403)**: Revisa tu token de acceso (validez, scopes correctos: `openid`, `profile`, `w_member_social`) y que los productos necesarios estén activos en tu app de LinkedIn.
-   **Errores de OpenAI**: Verifica tu clave API de OpenAI y el estado de tu cuenta (créditos, límites).
-   **Errores de NewsAPI**: Confirma tu API key de NewsAPI y que tu plan permite las consultas que estás haciendo (revisa el endpoint `/everything` y sus parámetros).
-   **Problemas con Google Search API**: Confirma tu clave API, ID de motor de búsqueda, y que la API esté habilitada en Google Cloud Console.

🤝 Contribuciones
-----------------

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir cambios o envía un *pull request*.

📜 Licencia
-----------

Este proyecto está licenciado bajo la Licencia MIT. Verifica el archivo `LICENSE` para más detalles.
