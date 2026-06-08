import time
from conn_sharepoint import get_auth_token, get_file_from_sharepoint, upload_file_to_sharepoint

class Sharepoint:

    def __init__(self):
        self.token = get_auth_token()

    def download_file(self, file_name, folder_name = ''):
        """
        Descarga un archivo desde una carpeta específica de SharePoint.

        Args:
            file_name (str): Nombre del archivo a descargar.
            folder_name (str): Nombre de la carpeta dentro de la biblioteca de documentos.

        Returns:
            bytes: El contenido del archivo en formato binario si la descarga es exitosa.
            None: Si ocurre un error durante la descarga.
        """

        try:
            # Obtiene la referencia al archivo usando la URL relativa
            file = get_file_from_sharepoint(file_name, self.token)
            # Devuelve el contenido binario del archivo
            return file.content
        
        except Exception as e:
            # Si ocurre un error, lo muestra y devuelve None
            print(f"Error al descargar el archivo {file_name} de SharePoint: {e}")
            return None
    
    def upload_file(self, file_name, content_stream, content_type = None,
                    folder_name = '', max_intentos = 3, espera = 5):
        """Sube un archivo binario a SharePoint vía Graph (PUT .../:/content).

        Devuelve el `webUrl` del archivo subido (link para abrirlo), o `None`
        si la subida falló. El flujo de Excel ignora el retorno; el de informes
        lo usa para construir el hipervínculo en la tabla OTS.

        Reintenta ante bloqueo (HTTP 423 / SPFileLockException), que ocurre
        cuando el archivo está abierto por alguien en SharePoint.
        """

        for intento in range(1, max_intentos + 1):
            try:
                content_stream.seek(0)  # Asegura que el stream esté al inicio
                response = upload_file_to_sharepoint(
                    file_name, self.token, content_stream.getvalue(), content_type)

                if response.status_code in (200, 201):
                    # El PUT a :/content devuelve el DriveItem en JSON, con webUrl.
                    try:
                        web_url = response.json().get('webUrl')
                    except Exception:
                        web_url = None
                    print(f"\n-> Archivo '{file_name}' subido con éxito")
                    return web_url

                if response.status_code == 423:
                    print(f"'{file_name}' bloqueado (423). Reintento {intento}/{max_intentos} en {espera}s...")
                    time.sleep(espera)
                    continue

                # Otro error HTTP: no tiene sentido reintentar.
                print(f"Error al subir '{file_name}': HTTP {response.status_code} - {response.text[:300]}")
                return None

            except Exception as e:
                error_str = str(e)
                if "SPFileLockException" in error_str or "423 Client Error: Locked" in error_str:
                    print(f"'{file_name}' bloqueado. Reintento {intento}/{max_intentos} en {espera}s...")
                    time.sleep(espera)
                    continue
                print(f"Error al subir el archivo a SharePoint: {error_str}")
                return None

        print(f"No se pudo subir '{file_name}': el archivo sigue bloqueado tras {max_intentos} intentos.")
        return None
