import streamlit as st
import os
import re
from PIL import Image
import tempfile

# Importar tus clases y funciones de lógica de negocio
# Asegúrate de que el archivo linkedin_post_automation.py esté en el mismo directorio o en PYTHONPATH
from linkedin_post_automation import LinkedInPostAutomation, get_env_variable_st
# (Si LinkedInAPIService es usada directamente por Streamlit, también importarla)

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


# Solo mostrar la UI si las variables de entorno están cargadas
if st.session_state.get('env_vars_loaded', False):
    automation = st.session_state.automation_instance

    # --- Sección de Entrada del Tema ---
    st.header("1. Define el Tema del Post")
    topic = st.text_input("Ingresa el tema para tu post de LinkedIn:", key="topic_input", placeholder="Ej: Impacto de la IA en la educación")

    if st.button("✨ Generar Contenido y Vista Previa", key="generate_button"):
        if not topic:
            st.warning("Por favor, ingresa un tema.")
        else:
            with st.spinner("Generando... Buscando información, creando texto e imagen... ⏳"):
                try:
                    # Llamar a la lógica de negocio que ahora lanza excepciones
                    results = automation.run_logic_for_streamlit(topic)
                    
                    st.session_state.generated_content = results["cleaned_text"]
                    st.session_state.cleaned_text_for_publish = results["cleaned_text"] # Inicializar con el texto limpiado
                    st.session_state.image_url = results["dalle_image_url"]
                    st.session_state.image_path_temp = results["temp_image_path"]
                    
                    st.success("Contenido y vista previa generados exitosamente.")
                    
                except Exception as e:
                    st.error(f"Ocurrió un error durante la generación: {e}")
                    # Limpiar estado parcial si falla la generación
                    st.session_state.generated_content = ""
                    st.session_state.image_url = None
                    st.session_state.image_path_temp = None
                    st.session_state.cleaned_text_for_publish = ""


    # --- Sección de Vista Previa y Edición ---
    if st.session_state.generated_content:
        st.header("2. Vista Previa y Edición")
        
        # Usar el valor de session_state para el text_area para que persista la edición
        edited_text_from_area = st.text_area(
            "Edita el texto del post:", 
            value=st.session_state.cleaned_text_for_publish, # Usar el texto que podría haber sido editado
            height=300, # Aumentar altura
            key="text_edit_area"
        )
        # Actualizar el estado de sesión con el texto editado inmediatamente
        st.session_state.cleaned_text_for_publish = edited_text_from_area

        if st.session_state.image_path_temp and os.path.exists(st.session_state.image_path_temp):
            try:
                # image_pil = Image.open(st.session_state.image_path_temp)
                st.image(st.session_state.image_path_temp, caption="Imagen Generada", use_container_width=True) # MODIFICADO AQUÍ
            except Exception as e:
                st.warning(f"No se pudo mostrar la imagen local: {e}. Ruta: {st.session_state.image_path_temp}")
        elif st.session_state.image_url: # Fallback a la URL de DALL-E si el archivo local no está
             st.image(st.session_state.image_url, caption="Imagen Generada (desde URL DALL-E)", use_container_width=True) # MODIFICADO AQUÍ


        # --- Sección de Confirmación y Publicación ---
        st.header("3. Confirmar y Publicar")
        if st.button("🚀 Publicar en LinkedIn", key="publish_button"):
            final_text_to_publish = st.session_state.cleaned_text_for_publish # Usar el texto del text_area
            
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
                            # Limpiar estado para un nuevo post después de publicar
                            st.session_state.generated_content = ""
                            st.session_state.image_url = None
                            # La limpieza del archivo temporal ahora la maneja la lógica de negocio
                            automation.cleanup_temp_image(st.session_state.image_path_temp)
                            st.session_state.image_path_temp = None
                            st.session_state.cleaned_text_for_publish = ""
                            # Forzar un rerun para limpiar la UI (opcional, pero puede ser útil)
                            # st.experimental_rerun() # Descomentar si es necesario y disponible
                            st.rerun() # Nueva forma de forzar rerun
                        else:
                            # Este 'else' podría no alcanzarse si publish_to_linkedin lanza excepciones
                            st.error("Fallo al publicar en LinkedIn. La función de publicación no indicó éxito.")
                    except Exception as e:
                        st.error(f"Ocurrió un error durante la publicación: {e}")
    else:
        st.info("Ingresa un tema y haz clic en '✨ Generar Contenido y Vista Previa' para comenzar.")

else:
    st.warning("La aplicación no pudo iniciarse debido a errores de configuración (variables de entorno).")
    st.markdown("Por favor, asegúrate de que tu archivo `.env` está correctamente configurado en el mismo directorio que el script y contiene todas las claves necesarias.")

# --- Para ejecutar la app de Streamlit ---
# Guarda este código como st_linkedin_app.py (o el nombre que prefieras)
# Ejecuta desde la terminal: streamlit run st_linkedin_app.py
