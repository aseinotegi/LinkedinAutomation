import streamlit as st
import os
import re
from PIL import Image
import tempfile

# Importar tus clases y funciones de lógica de negocio
# Asegúrate de que el archivo linkedin_post_automation.py esté en el mismo directorio o en PYTHONPATH
from linkedin_post_automation import LinkedInPostAutomation, get_env_variable_st
# (Si LinkedInAPIService es usada directamente por Streamlit, también importarla si es necesario)

# --- Configuración de la Página de Streamlit ---
st.set_page_config(page_title="LinkedIn Post Automator", layout="wide")
st.title("🤖 Automatizador de Posts para LinkedIn con IA")
st.markdown("Genera y publica contenido en LinkedIn de forma automatizada.")

# --- Inicializar el estado de la sesión ---
if 'automation_instance' not in st.session_state:
    try:
        # Cargar variables de entorno primero para asegurar que existen
        get_env_variable_st("OPENAI_API_KEY")
        get_env_variable_st("SEARCH_API_KEY")
        get_env_variable_st("SEARCH_ENGINE_ID")
        get_env_variable_st("LINKEDIN_ACCESS_TOKEN")
        get_env_variable_st("LINKEDIN_USER_URN")
        get_env_variable_st("NEWSAPI_KEY") # Asegúrate que LinkedInPostAutomation lo usa
        
        st.session_state.automation_instance = LinkedInPostAutomation()
        st.session_state.env_vars_loaded = True
    except ValueError as e:
        st.error(str(e))
        st.session_state.env_vars_loaded = False
    except Exception as e: # Otras excepciones durante la inicialización
        st.error(f"Error al inicializar la automatización: {e}")
        st.session_state.env_vars_loaded = False
        
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'image_path_temp' not in st.session_state:
    st.session_state.image_path_temp = None
if 'cleaned_text_for_publish' not in st.session_state:
    st.session_state.cleaned_text_for_publish = ""
if 'topic_input_value' not in st.session_state: # <--- AÑADIDO para el input del tema
    st.session_state.topic_input_value = ""
if 'suggested_topics' not in st.session_state: # <--- AÑADIDO para guardar las sugerencias
    st.session_state.suggested_topics = []


# Solo mostrar la UI si las variables de entorno están cargadas
if st.session_state.get('env_vars_loaded', False):
    automation = st.session_state.automation_instance

    # --- Sección de Descubrir Temas en la Sidebar ---
    st.sidebar.header("💡 Descubrir Temas")
    if st.sidebar.button("Buscar Noticias de IA (Global)"):
        with st.spinner("Buscando noticias de IA..."):
            # Llama al método en la instancia de LinkedInPostAutomation
            # Ajusta los parámetros según necesites
            news_items = automation.get_news_suggestions(
                keywords='IA OR "inteligencia artificial"', # O lo que quieras probar
                language='es',                             # o 'en'
                sort_by='publishedAt',                     # o 'popularity', 'relevancy'
                num_articles=10,
                days_ago=28                                # Por ejemplo, últimos 28 días
            )
            if news_items:
                st.session_state.suggested_topics = news_items
                if not news_items: # Comprobar si la lista está vacía incluso si la llamada fue exitosa
                    st.sidebar.info("No se encontraron artículos para los criterios seleccionados.")
            else:
                st.sidebar.warning("No se pudieron obtener noticias o hubo un error en la búsqueda.")

    if st.session_state.suggested_topics:
        st.sidebar.subheader("Temas Sugeridos:")
        for i, item in enumerate(st.session_state.suggested_topics):
            # Asegúrate de que item tiene 'title' y 'source', o maneja el caso de que falten
            title = item.get('title', 'Título no disponible')
            source = item.get('source', 'Fuente no disponible')
            if st.sidebar.button(f"{title} (Fuente: {source})", key=f"suggest_{i}"):
                st.session_state.topic_input_value = title  # Actualiza el valor para el text_input
                st.sidebar.info(f"Tema '{title}' seleccionado. Edítalo si es necesario y genera el contenido.")
                # Opcional: Limpiar sugerencias después de seleccionar una
                # st.session_state.suggested_topics = [] 
                # st.experimental_rerun() # Para actualizar la UI inmediatamente si limpias sugerencias

    # --- Sección de Entrada del Tema (en el cuerpo principal)---
    st.header("1. Define el Tema del Post")
    
    # Usar st.session_state.topic_input_value para el input del tema
    # La variable 'topic' se actualizará con el valor actual del input field
    topic = st.text_input(
        "Ingresa el tema para tu post de LinkedIn:", 
        value=st.session_state.topic_input_value, # Usa el valor de session_state
        key="topic_input_main", # Cambiado para evitar conflicto con 'topic_input' si se usaba antes
        placeholder="Ej: Impacto de la IA en la educación",
        on_change=lambda: setattr(st.session_state, 'topic_input_value', st.session_state.topic_input_main) # Actualiza el session_state si el usuario escribe
    )
    # Sincronizar el valor del widget con session_state.topic_input_value
    # Esto es importante si el valor se cambia programáticamente (ej. al hacer clic en un tema sugerido)
    # y también si el usuario escribe directamente.
    # La forma más robusta con `on_change` es preferible.
    # Si no se usa on_change, la lógica original era:
    # if topic != st.session_state.topic_input_value:
    #    st.session_state.topic_input_value = topic
    # Actualizamos 'topic' para que refleje el valor de session_state que podría haber cambiado
    topic = st.session_state.topic_input_value


    if st.button("✨ Generar Contenido y Vista Previa", key="generate_button"):
        if not topic: # Ahora 'topic' siempre refleja el contenido de topic_input_value
            st.warning("Por favor, ingresa un tema.")
        else:
            with st.spinner("Generando... Buscando información, creando texto e imagen... ⏳"):
                try:
                    results = automation.run_logic_for_streamlit(topic) # Usar la variable 'topic' actualizada
                    
                    st.session_state.generated_content = results["cleaned_text"]
                    st.session_state.cleaned_text_for_publish = results["cleaned_text"]
                    st.session_state.image_url = results["dalle_image_url"]
                    st.session_state.image_path_temp = results["temp_image_path"]
                    
                    st.success("Contenido y vista previa generados exitosamente.")
                    
                except Exception as e:
                    st.error(f"Ocurrió un error durante la generación: {e}")
                    st.session_state.generated_content = ""
                    st.session_state.image_url = None
                    st.session_state.image_path_temp = None
                    st.session_state.cleaned_text_for_publish = ""

    # --- Sección de Vista Previa y Edición ---
    if st.session_state.generated_content:
        st.header("2. Vista Previa y Edición")
        
        edited_text_from_area = st.text_area(
            "Edita el texto del post:", 
            value=st.session_state.cleaned_text_for_publish,
            height=300,
            key="text_edit_area"
        )
        st.session_state.cleaned_text_for_publish = edited_text_from_area

        if st.session_state.image_path_temp and os.path.exists(st.session_state.image_path_temp):
            try:
                st.image(st.session_state.image_path_temp, caption="Imagen Generada", use_container_width=True)
            except Exception as e:
                st.warning(f"No se pudo mostrar la imagen local: {e}. Ruta: {st.session_state.image_path_temp}")
        elif st.session_state.image_url:
             st.image(st.session_state.image_url, caption="Imagen Generada (desde URL DALL-E)", use_container_width=True)

        # --- Sección de Confirmación y Publicación ---
        st.header("3. Confirmar y Publicar")
        if st.button("🚀 Publicar en LinkedIn", key="publish_button"):
            final_text_to_publish = st.session_state.cleaned_text_for_publish
            
            if not final_text_to_publish or not st.session_state.image_path_temp:
                st.error("No hay texto o imagen para publicar. Asegúrate de que la imagen se haya generado y guardado localmente.")
            elif not os.path.exists(st.session_state.image_path_temp):
                 st.error(f"El archivo de imagen temporal no se encuentra en: {st.session_state.image_path_temp}. Intenta generar de nuevo.")
            else:
                with st.spinner("Publicando en LinkedIn... ⏳"):
                    try:
                        success, post_id = automation.publish_to_linkedin(
                            final_text_to_publish, 
                            st.session_state.image_path_temp
                        )
                        if success:
                            st.success(f"¡Post publicado exitosamente en LinkedIn! ID del Post: {post_id}")
                            st.balloons()
                            st.session_state.generated_content = ""
                            st.session_state.image_url = None
                            automation.cleanup_temp_image(st.session_state.image_path_temp)
                            st.session_state.image_path_temp = None
                            st.session_state.cleaned_text_for_publish = ""
                            st.session_state.topic_input_value = "" # Limpiar también el tema
                            st.session_state.suggested_topics = [] # Limpiar sugerencias
                            st.rerun()
                        else:
                            st.error("Fallo al publicar en LinkedIn. La función de publicación no indicó éxito.")
                    except Exception as e:
                        st.error(f"Ocurrió un error durante la publicación: {e}")
    else:
        st.info("Ingresa un tema y haz clic en '✨ Generar Contenido y Vista Previa' para comenzar, o busca temas en la barra lateral.")

else:
    st.warning("La aplicación no pudo iniciarse debido a errores de configuración (variables de entorno).")
    st.markdown("Por favor, asegúrate de que tu archivo `.env` está correctamente configurado en el mismo directorio que el script y contiene todas las claves necesarias.")

# --- Para ejecutar la app de Streamlit ---
# Guarda este código como st_linkedin_app.py (o el nombre que prefieras)
# Ejecuta desde la terminal: streamlit run st_linkedin_app.py