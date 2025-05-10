import requests
import json

# Pega aquí tu LINKEDIN_ACCESS_TOKEN obtenido
LINKEDIN_ACCESS_TOKEN = "AQUwZuUIcTjSJD5sQrhY8APuRL31XA-IgT94rqKxX6jC2useesU0VDIu-1D0EzRq1ZPO6JszEU_dtklJMmDcF0ODM3zmyj521qsCXGuqaZ4dTCA5NcMVG1fyiZPCjZtAtYMptKQa_JEY577n5SBIn0wzMOKkCFLJxRoG3h_BAiJ4vHGBJWYCdHZIop76bSKUMPSkQrVH0TWMlUyEtk-bxrc0iNUVBgcMeKRyWVbixHVFOtF6z8cyFx6cTGWozpkTeaTX_ToscFfzOudrpI6zs2uz5n8iYt7yrOe_DwCiz-Y8iyH2it3EYnt5tLDky2mypEBCUyqJSF_3WrUf_-xLOIMHx9GPXg" # Asegúrate de poner el token más reciente

if LINKEDIN_ACCESS_TOKEN != LINKEDIN_ACCESS_TOKEN or not LINKEDIN_ACCESS_TOKEN:
    print("Error: Por favor, reemplaza 'PEGA_AQUI_TU_NUEVO_TOKEN_DE_ACCESO' con tu token real en el script.")
else:
    # Vamos a usar el endpoint /v2/userinfo, que es común con OpenID Connect
    url = "https://api.linkedin.com/v2/userinfo"

    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    # Para /v2/userinfo, generalmente no se requieren los headers LinkedIn-Version o X-Restli-Protocol-Version,
    # solo el token de autorización.

    print(f"Intentando llamar a: {url}")
    print(f"Usando token que empieza con: {LINKEDIN_ACCESS_TOKEN[:15]}...")

    try:
        response = requests.get(url, headers=headers)
        print(f"Código de estado de la respuesta: {response.status_code}") # Para depurar
        response.raise_for_status()  # Esto generará un error si la solicitud HTTP falló

        profile_data = response.json()
        # print("\nRespuesta completa del perfil:") # Descomenta para depurar
        # print(json.dumps(profile_data, indent=2))

        # Con /v2/userinfo, el ID del usuario suele estar en el campo "sub" (subject)
        if "sub" in profile_data:
            user_id = profile_data["sub"]
            linkedin_user_urn = f"urn:li:person:{user_id}"
            print(f"\nTu LINKEDIN_USER_URN es: {linkedin_user_urn}")
            print(f"\nCopia este valor en tu archivo .env para la variable LINKEDIN_USER_URN.")
        else:
            print("\nError: No se pudo encontrar el campo 'sub' (ID de usuario) en la respuesta de la API.")
            print("Respuesta obtenida:")
            print(json.dumps(profile_data, indent=2))

    except requests.exceptions.HTTPError as http_err:
        print(f"\nError HTTP: {http_err}")
        # print(f"Código de estado: {response.status_code}") # Ya se imprime arriba
        try:
            error_details = response.json()
            print("Detalles del error:")
            print(json.dumps(error_details, indent=2))
        except json.JSONDecodeError:
            print("Cuerpo de la respuesta (no es JSON):")
            print(response.text)
    except Exception as err:
        print(f"\nOcurrió otro error: {err}")