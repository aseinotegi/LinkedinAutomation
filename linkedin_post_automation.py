#!/usr/bin/env python3
"""
LinkedIn Post Automation Script (Refactored for GUI/Streamlit use)

This script automates the creation and publication of posts on LinkedIn using:
- Search API to get relevant information about a topic
- OpenAI to generate text content
- OpenAI DALL-E to generate related images
- LinkedIn API to publish content (using /rest/images and /rest/posts)

Original Author: Automatización LinkedIn
Adaptations for GUI/Streamlit: AI Assistant
Date: May 2025
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import tempfile
import re
import datetime

# --- Load Environment Variables ---
load_dotenv()
    
# --- Modified Function to Get Environment Variables for GUI/Streamlit ---
def get_env_variable_st(var_name):
    """
    Gets an environment variable. Raises ValueError if not found.
    This allows the calling application (e.g., Streamlit) to handle the error.
    """
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Error: Environment variable {var_name} not found. "
                         "Please configure all required environment variables in the .env file.")
    return value

# --- LinkedIn API Service Class ---
class LinkedInAPIService:
    """
    Handles interactions with the LinkedIn API.
    Progress/error messages can be printed to a passed console
    or could be refactored to return (success, message/data) tuples for pure GUI.
    """
    def __init__(self, access_token, user_urn, newsapi_key, api_version="202504", console_instance=None):
        self.access_token = access_token
        self.user_urn = user_urn
        self.newsapi_key = newsapi_key
        self.api_version = api_version
        # If no console is passed (e.g., from a pure GUI), prints won't happen here.
        # For Streamlit, a console passed from LinkedInPostAutomation would print to Streamlit's terminal.
        self.console = console_instance

    def _print_console(self, message, style=""): # Helper method to print if console exists
        if self.console:
            # This uses rich.console.Console. If self.console is None, it does nothing.
            # For Streamlit, if you want these messages in the GUI, this class should return them.
            # For now, they will go to the terminal where Streamlit is run if a console is passed.
            try:
                if style:
                    self.console.print(f"[{style}]{message}[/{style}]")
                else:
                    self.console.print(message)
            except Exception: # Fallback if console object doesn't support Rich print
                print(message)

    def fetch_ai_news_from_newsapi(self,keywords='artificial intelligence', language='es',  sort_by='popularity', num_articles=10, days_ago=30):
        """
        Obtiene noticias sobre IA usando NewsAPI.
        """
        if not self.newsapi_key:
            # Usar self._print_console si está disponible y configurado
            message = "Advertencia: NEWSAPI_KEY no configurada para LinkedInAPIService."
            if self.console and hasattr(self.console, 'print'):
                self._print_console(message, style="bold orange")
            else:
                print(message)
            return []

        # Calcular la fecha 'desde' (from_date) usando el parámetro days_ago
        try:
            from_date = (datetime.date.today() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d')
        except Exception as e:
            message = f"Error al calcular from_date: {e}"
            if self.console and hasattr(self.console, 'print'):
                self._print_console(message, style="bold red")
            else:
                print(message)
            return []

        # ... (resto de tu lógica para la URL)
        
        url = (f"https://newsapi.org/v2/everything?"
               f"q={keywords}&"
               f"from={from_date}&"
               f"sortBy={sort_by}&"
               f"language={language}&"
               f"apiKey={self.newsapi_key}&"
               f"pageSize={num_articles}")
        
        # Imprimir URL para depuración (opcional, puedes quitarlo después)
        url_message = f"NewsAPI URL: {url}"
        if self.console and hasattr(self.console, 'print'):
            self._print_console(url_message, style="cyan")
        else:
            print(url_message)

        try:
            response = requests.get(url)
            response.raise_for_status() 
            
            data = response.json()
            
            # Imprimir respuesta completa para depuración (opcional, puedes quitarlo después)
            # data_message = f"NewsAPI Response Data: {data}"
            # if self.console and hasattr(self.console, 'print'):
            #     self._print_console(data_message, style="magenta")
            # else:
            #     print(data_message)

            articles = data.get("articles", [])
            
            if not articles:
                no_articles_message = f"No se encontraron artículos para: q='{keywords}', from='{from_date}', lang='{language}', sortBy='{sort_by}'."
                if self.console and hasattr(self.console, 'print'):
                    self._print_console(no_articles_message, style="yellow")
                else:
                    print(no_articles_message)

            news_suggestions = []
            for article in articles:
                news_suggestions.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name")
                })
            return news_suggestions
        except requests.exceptions.HTTPError as http_err:
            error_body = http_err.response.text if http_err.response else 'No response body'
            http_error_message = f"Error HTTP al obtener noticias de NewsAPI: {http_err}. Response: {error_body}"
            if self.console and hasattr(self.console, 'print'):
                self._print_console(http_error_message, style="bold red")
            else:
                print(http_error_message)
            return []
        except Exception as e:
            exception_message = f"Error inesperado en fetch_ai_news_from_newsapi: {e}"
            if self.console and hasattr(self.console, 'print'):
                self._print_console(exception_message, style="bold red")
            else:
                print(exception_message)
            return []
    
    def initialize_image_upload(self):
        """Step 1: Initializes the image upload to LinkedIn."""
        self._print_console("  Iniciando subida de imagen a LinkedIn...")
        init_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0", # Often required for /rest/ APIs
            "LinkedIn-Version": self.api_version
        }
        payload = {
            "initializeUploadRequest": {
                "owner": self.user_urn
            }
        }
        
        try:
            response = requests.post(init_url, headers=headers, json=payload)
            self._print_console(f"    Respuesta de inicialización (paso 1): {response.status_code}")
            response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
            data = response.json()
            
            upload_url = data.get("value", {}).get("uploadUrl")
            image_urn = data.get("value", {}).get("image")

            if not upload_url or not image_urn:
                error_msg = f"Error: La respuesta de initializeUpload no contenía uploadUrl o image URN. Data: {data}"
                self._print_console(error_msg, style="bold red")
                raise Exception(error_msg) # Propagate error
            
            self._print_console(f"    Image URN (obtenido): {image_urn}")
            self._print_console(f"    Upload URL (parcial): {upload_url[:70]}...")
            return upload_url, image_urn
        except requests.exceptions.HTTPError as http_err:
            error_body = http_err.response.text if http_err.response else 'No response body'
            self._print_console(f"Error HTTP durante la inicialización de subida de imagen: {http_err}", style="bold red")
            self._print_console(f"    Respuesta del servidor: {error_body}")
            raise Exception(f"Error HTTP inicializando subida: {http_err} - {error_body}") from http_err
        except Exception as e:
            self._print_console(f"Error general durante la inicialización de subida de imagen: {str(e)}", style="bold red")
            raise Exception(f"Error general inicializando subida: {str(e)}") from e

    def upload_image_data(self, upload_url, image_path):
        """Step 2: Uploads the image data to the provided URL."""
        self._print_console("  Subiendo datos de la imagen...")
        try:
            with open(image_path, 'rb') as image_file_data:
                img_data = image_file_data.read()
            
            # The Authorization header might be optional for the direct PUT to Azure/S3,
            # but LinkedIn's examples sometimes include it or it's benignly ignored.
            headers = {
                "Authorization": f"Bearer {self.access_token}", 
                "Content-Type": "application/octet-stream"
            }
            
            response = requests.put(upload_url, headers=headers, data=img_data)
            self._print_console(f"    Respuesta de subida de imagen (paso 2): {response.status_code}")
            response.raise_for_status()
            self._print_console("  ✓ Imagen subida correctamente a LinkedIn.", style="green")
            return True # Indicate success
        except requests.exceptions.HTTPError as http_err:
            error_body = http_err.response.text if http_err.response else 'No response body'
            self._print_console(f"Error HTTP al subir la imagen: {http_err}", style="bold red")
            self._print_console(f"    Respuesta del servidor: {error_body}")
            raise Exception(f"Error HTTP subiendo imagen: {http_err} - {error_body}") from http_err
        except Exception as e:
            self._print_console(f"Error al subir la imagen: {str(e)}", style="bold red")
            raise Exception(f"Error general subiendo imagen: {str(e)}") from e

    def create_post_with_image(self, text_content, image_urn):
        """Step 3: Creates the post on LinkedIn with the text and image URN (using /rest/posts)."""
        self._print_console("  Creando el post en LinkedIn con la imagen (usando /rest/posts)...")
        post_url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8", # Specify charset for robustness
            "LinkedIn-Version": self.api_version
            # "X-Restli-Protocol-Version": "2.0.0" # Usually not strictly needed for /rest/posts
        }
        payload = {
            "author": self.user_urn,
            "commentary": text_content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "content": {
                "media": {
                    "id": image_urn
                    # "title": f"Imagen sobre {text_content[:30]}..." # Optional media title
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        self._print_console("DEBUG: Enviando el siguiente texto en 'commentary':", style="bold cyan")
        self._print_console(text_content) 
            
        try:
            response = requests.post(post_url, headers=headers, json=payload)
            self._print_console(f"    Respuesta de creación de post (paso 3): {response.status_code}")
            
            if response.status_code == 201: # 201 Created
                post_id = response.headers.get("x-linkedin-id") or response.headers.get("x-restli-id")
                self._print_console(f"  ✓ Post publicado correctamente. ID: {post_id}", style="green")
                return True, post_id # Return success and post ID
            else:
                # This will be caught by the HTTPError exception if status is 4xx/5xx
                response.raise_for_status() 
                # Should not reach here if raise_for_status works
                raise Exception(f"Error creando post: Código de estado {response.status_code} - {response.text}")
        except requests.exceptions.HTTPError as http_err:
            error_body = http_err.response.text if http_err.response else 'No response body'
            self._print_console(f"Error HTTP al crear el post: {http_err}", style="bold red")
            self._print_console(f"    Respuesta del servidor: {error_body}")
            raise Exception(f"Error HTTP creando post: {http_err} - {error_body}") from http_err
        except Exception as e:
            self.console.print(f"Error al crear el post: {str(e)}", style="bold red")
            raise Exception(f"Error general creando post: {str(e)}") from e

# --- Main Automation Class ---
class LinkedInPostAutomation:
    def __init__(self):
        """Initializes the class with API credentials and configurations."""
        # For use with Streamlit, get_env_variable_st errors will propagate
        self.openai_api_key = get_env_variable_st("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        self.search_api_key = get_env_variable_st("SEARCH_API_KEY")
        self.search_engine_id = get_env_variable_st("SEARCH_ENGINE_ID")
        
        linkedin_access_token = get_env_variable_st("LINKEDIN_ACCESS_TOKEN")
        linkedin_user_urn = get_env_variable_st("LINKEDIN_USER_URN")
        
        self.newsapi_key_for_service = get_env_variable_st("NEWSAPI_KEY")
        # For Streamlit, you might pass None if you don't want API service logs in Streamlit's terminal,
        # or pass a Rich Console instance if you do want detailed API logs there.
        # from rich.console import Console # Import if using Rich Console here
        # self.console_for_api_service = Console() 
        self.console_for_api_service = None # Set to None to suppress LinkedInAPIService prints to terminal

        self.linkedin_service = LinkedInAPIService(
            access_token=linkedin_access_token,
            user_urn=linkedin_user_urn,
            newsapi_key=self.newsapi_key_for_service,
            api_version=os.getenv("LINKEDIN_API_VERSION", "202504"), # Load from .env or default
            console_instance=self.console_for_api_service
        )
        
    def get_news_suggestions(self, keywords='artificial intelligence', language='es', sort_by='popularity', num_articles=10, days_ago=30):
        """
        Obtiene sugerencias de noticias llamando al método correspondiente en linkedin_service.
        """
        return self.linkedin_service.fetch_ai_news_from_newsapi(
                        keywords=keywords,           
                        language=language,         
                        sort_by=sort_by,           
                        num_articles=num_articles, 
                        days_ago=days_ago          
                    )
        
        # Este bloque solo se ejecutaría si self.linkedin_service no estuviera inicializado
        # (lo cual no debería pasar si __init__ funciona bien)
        if self.console_for_api_service and hasattr(self.console_for_api_service, 'print'):
            self.console_for_api_service.print("Advertencia: LinkedInAPIService no está inicializado en LinkedInPostAutomation al llamar a get_news_suggestions.", style="bold orange")
        else:
            print("Advertencia: LinkedInAPIService no está inicializado en LinkedInPostAutomation al llamar a get_news_suggestions.")
        return []
        
    def search_topic(self, topic, num_results=5):
        """Searches for relevant information on a topic using Google Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.search_api_key, "cx": self.search_engine_id,
                "q": topic, "num": num_results
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            search_results = response.json()
            context = ""
            if "items" in search_results:
                for item in search_results["items"]:
                    context += f"Título: {item.get('title', '')}\nResumen: {item.get('snippet', '')}\nEnlace: {item.get('link', '')}\n\n"
            if not context: 
                return f"No se encontró información relevante sobre '{topic}'." # Return as string for Streamlit
            return context
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al buscar información en Google: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Error inesperado en search_topic: {str(e)}") from e

    def generate_post_content(self, topic, context):
        """Generates post content using OpenAI."""
        try:
            prompt = f"""
            Crea un post profesional para LinkedIn sobre el tema: {topic}.
            El post debe:
            1. Tener 3 párrafos medianos (no más de 3-4 oraciones cada uno)
            2. Ser informativo y atractivo para profesionales
            3. Incluir algún dato o estadística relevante
            4. Terminar con una pregunta o llamado a la acción
            5. No exceder los 1500 caracteres en total
            Usa esta información como contexto:
            {context}
            Formato: Solo el texto del post, sin títulos ni etiquetas adicionales.
            """
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "Eres un experto en marketing digital y creación de contenido para LinkedIn."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", 1000)),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.7))
            )
            post_content = response.choices[0].message.content.strip()
            return post_content
        except Exception as e:
            raise Exception(f"Error al generar contenido con OpenAI: {str(e)}") from e

    def generate_image(self, topic):
        """Generates an image related to the topic using DALL-E."""
        temp_image_obj = None # To hold the NamedTemporaryFile object
        try:
            prompt = f"Una imagen profesional y atractiva para un post de LinkedIn sobre {topic}. Estilo corporativo, alta calidad, adecuada para redes profesionales."
            response = self.openai_client.images.generate(
                model=os.getenv("DALLE_MODEL", "dall-e-3"),
                prompt=prompt,
                size="1024x1024", quality="standard", n=1
            )
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Create a temporary file to store the image
            temp_image_obj = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_image_obj.write(image_response.content)
            image_path_temp = temp_image_obj.name # Get the path
            return image_url, image_path_temp
        except Exception as e:
            raise Exception(f"Error al generar imagen con DALL-E: {str(e)}") from e
        finally:
            if temp_image_obj: # Ensure the file is closed if it was created
                temp_image_obj.close()

    def publish_to_linkedin(self, text_content, image_path):
        """
        Publishes the content to LinkedIn.
        Uses the LinkedInAPIService instance to handle API logic.
        Returns True and post_id on success, or raises an exception on failure.
        """
        upload_url, image_urn = self.linkedin_service.initialize_image_upload()
        # initialize_image_upload will raise an exception if it fails

        self.linkedin_service.upload_image_data(upload_url, image_path)
        # upload_image_data will raise an exception if it fails
        
        success, post_id = self.linkedin_service.create_post_with_image(text_content, image_urn)
        # create_post_with_image will raise an exception if it fails, or return True, post_id
        
        return success, post_id # Propagate success and post_id

    def run_logic_for_streamlit(self, topic):
        """
        Executes the main logic flow to be called from Streamlit.
        Returns results or raises exceptions.
        Does not handle user interaction (input, approval) or GUI.
        """
        # STEP 1: SEARCH
        context = self.search_topic(topic)
        # (Error handling is now by exceptions in search_topic)

        # STEP 2: GENERATE POST CONTENT
        post_content_raw = self.generate_post_content(topic, context)

        # STEP 2.5: CLEAN TEXT
        text_cleaned = post_content_raw.replace('\r\n', '\n').replace('\r', '\n')
        text_cleaned = re.sub(r'\n{3,}', '\n\n', text_cleaned)
        lines = text_cleaned.split('\n')
        lines_cleaned = [line.strip() for line in lines]
        post_content_cleaned = '\n'.join(lines_cleaned).strip()
        
        # STEP 3: GENERATE IMAGE
        image_url_dalle, image_path_temp = self.generate_image(topic)
        # (If generate_image fails, it will raise an exception)

        return {
            "original_text": post_content_raw,
            "cleaned_text": post_content_cleaned,
            "dalle_image_url": image_url_dalle,
            "temp_image_path": image_path_temp
        }

    def cleanup_temp_image(self, image_path_temp):
        """Cleans up the temporary image file."""
        if image_path_temp and os.path.exists(image_path_temp):
            try:
                os.unlink(image_path_temp)
                # print(f"Imagen temporal {image_path_temp} eliminada.") # Optional: log for Streamlit console
                return True
            except Exception as e_unlink:
                # print(f"Advertencia: No se pudo eliminar imagen temporal {image_path_temp}. Error: {e_unlink}")
                # In a GUI, this error could be logged or subtly displayed
                # For now, just indicate failure to delete
                return False 
        return True # Return True if no file to delete or deletion was successful


# The original main() function with argparse can be kept for command-line use
# if desired, but it won't be used directly when running with Streamlit.
# If kept, it would need its own Console, Panel, etc. instantiation.
# For example:
#
# from rich.console import Console as RichConsole
# from rich.panel import Panel as RichPanel
# from rich.markdown import Markdown as RichMarkdown
# import argparse as ArgParseForCLI

# def main_cli():
#     """Command-line interface main function."""
#     cli_console = RichConsole()
#     parser = ArgParseForCLI.ArgumentParser(description='Automatización de posts en LinkedIn (CLI)')
#     parser.add_argument('--topic', '-t', type=str, help='Tema del post a generar')
#     args = parser.parse_args()
    
#     topic = args.topic
#     if not topic:
#         cli_console.print("[bold blue]Ingresa el tema para el post de LinkedIn:[/bold blue]")
#         topic = input("> ").strip()
#         if not topic:
#             cli_console.print("[bold red]Error: Se requiere un tema para generar el post.[/bold red]")
#             sys.exit(1)
    
#     try:
#         automation = LinkedInPostAutomation() # This will use get_env_variable_st

#         # --- This is a simplified version of the original 'run' method for CLI ---
#         cli_console.print(RichPanel(f"[bold]Automatización de Post en LinkedIn (CLI)[/bold]\nTema: [italic]{topic}[/italic]", border_style="blue"))
        
#         cli_console.print("\n--- PASO 1: BÚSQUEDA DE INFORMACIÓN ---")
#         context = automation.search_topic(topic)
#         cli_console.print("[green]✓[/green] Contexto obtenido.")

#         cli_console.print("\n--- PASO 2: GENERACIÓN DE CONTENIDO DEL POST ---")
#         post_content_raw = automation.generate_post_content(topic, context)
#         cli_console.print("[green]✓[/green] Contenido del post generado.")
        
#         # Limpieza
#         text_cleaned = post_content_raw.replace('\r\n', '\n').replace('\r', '\n')
#         text_cleaned = re.sub(r'\n{3,}', '\n\n', text_cleaned)
#         lines = text_cleaned.split('\n')
#         lines_cleaned = [line.strip() for line in lines]
#         post_content_cleaned = '\n'.join(lines_cleaned).strip()
#         cli_console.print("[green]✓[/green] Texto limpiado.")

#         cli_console.print("\n--- PASO 3: GENERACIÓN DE IMAGEN ---")
#         image_url_dalle, image_path_temp = automation.generate_image(topic)
#         cli_console.print(f"[green]✓[/green] Imagen generada: {image_url_dalle}")

#         cli_console.print("\n--- PASO 4: VISTA PREVIA DEL POST ---")
#         cli_console.print(RichPanel(RichMarkdown(post_content_cleaned), border_style="green", title="Contenido del Post (Limpiado)"))
#         cli_console.print(f"[bold]Imagen (Ruta temporal):[/bold] {image_path_temp}")
        
#         # (Skipping Image.show() for CLI simplicity here, user can open manually)

#         cli_console.print("\n--- PASO 5: APROBACIÓN DEL USUARIO ---")
#         approval = input("\n¿Deseas publicar este post en LinkedIn? (y/N): ").strip().lower()

#         success_publish = False
#         if approval == 'y':
#             cli_console.print("\n--- PASO 6: PUBLICACIÓN EN LINKEDIN ---")
#             success_publish, post_id = automation.publish_to_linkedin(post_content_cleaned, image_path_temp)
#             if success_publish:
#                 cli_console.print(f"[green]✓ Publicado! Post ID: {post_id}[/green]")
#             else:
#                 cli_console.print("[red]✗ Fallo al publicar.[/red]")
#         else:
#             cli_console.print("[yellow]Publicación cancelada.[/yellow]")
        
#         automation.cleanup_temp_image(image_path_temp)

#         if success_publish:
#             cli_console.print("[bold green]\n¡Proceso completado exitosamente![/bold green]")
#         else:
#             cli_console.print("[bold red]\nEl proceso no se completó o fue cancelado.[/bold red]")

#     except ValueError as ve: # Captura errores de get_env_variable_st
#         cli_console.print(f"[bold red]Error de Configuración:[/bold red] {ve}")
#         sys.exit(1)
#     except Exception as e:
#         cli_console.print(f"[bold red]Ocurrió un error inesperado en el flujo CLI:[/bold red] {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     # main_cli() # Descomentar para ejecutar la versión de línea de comandos
#     pass # Dejar pass si este archivo solo va a ser importado por Streamlit
