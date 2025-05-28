"""
Operaciones de adjuntos para elementos de trabajo de Azure DevOps.

Este módulo proporciona herramientas MCP para descargar y gestionar adjuntos de work items.
"""
from typing import Dict, Any
import os

from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

from mcp_azure_devops.features.work_items.common import (
    AzureDevOpsClientError,
    get_work_item_client,
)


def _get_attachment_info_from_work_item(
    work_item_id: int,
    attachment_id: str,
    wit_client: WorkItemTrackingClient
) -> Dict[str, Any]:
    """
    Obtiene la información del adjunto desde el work item.
    
    Args:
        work_item_id: ID del elemento de trabajo
        attachment_id: ID del archivo adjunto
        wit_client: Cliente de work item tracking
    
    Returns:
        Diccionario con la información del adjunto
    """
    try:
        # Obtener el work item con sus relaciones
        work_item = wit_client.get_work_item(work_item_id, expand="relations")
        
        if not work_item or not work_item.relations:
            raise AzureDevOpsClientError(
                f"No se encontraron adjuntos en el work item {work_item_id}")
        
        # Buscar la relación que corresponde al adjunto
        for relation in work_item.relations:
            if (relation.rel == "AttachedFile" and 
                    attachment_id in relation.url):
                # Extraer el nombre del archivo de la URL
                filename = os.path.basename(relation.attributes.get("name", ""))
                return {
                    "name": filename,
                    "url": relation.url,
                    "attributes": relation.attributes
                }
        
        raise AzureDevOpsClientError(
            f"No se encontró el adjunto {attachment_id} en el work item {work_item_id}")
            
    except Exception as e:
        raise AzureDevOpsClientError(
            f"Error al obtener información del adjunto: {str(e)}")


def _download_attachment_impl(
    work_item_id: int,
    attachment_id: str,
    output_path: str,
    wit_client: WorkItemTrackingClient
) -> Dict[str, Any]:
    """
    Implementación de la descarga de un archivo adjunto.
    
    Args:
        work_item_id: ID del elemento de trabajo
        attachment_id: ID del archivo adjunto
        output_path: Ruta donde guardar el archivo descargado
        wit_client: Cliente de work item tracking
    
    Returns:
        Información sobre el archivo descargado
    """
    try:
        # Obtener información del adjunto desde el work item
        attachment_info = _get_attachment_info_from_work_item(
            work_item_id, attachment_id, wit_client)
        
        # Obtener el generador del contenido del adjunto
        attachment_content_generator = wit_client.get_attachment_content(attachment_id)
        
        downloads_dir = "/downloads"
        # Manejar rutas tanto de Windows como de Linux
        if "\\" in output_path or (":" in output_path and len(output_path.split(":")[0]) == 1):
            # Es una ruta de Windows, extraer el nombre del archivo
            filename = output_path.replace("\\", "/").split("/")[-1]
        else:
            # Es una ruta de Linux o solo un nombre de archivo
            filename = os.path.basename(output_path)
        
        final_path = os.path.join(downloads_dir, filename)

        # Asegurarse de que el directorio de salida existe
        os.makedirs(os.path.dirname(os.path.abspath(final_path)), exist_ok=True)
        
        # Guardar el contenido en un archivo iterando sobre el generador
        total_size = 0
        with open(final_path, 'wb') as f:
            # Iterar directamente sobre el generador
            for chunk in attachment_content_generator:
                f.write(chunk)
                total_size += len(chunk)
        
        return {
            "filename": attachment_info["name"],
            "size": total_size,
            "content_type": attachment_info["attributes"].get("contentType", "application/octet-stream"),
            "saved_to": final_path
        }
    except Exception as e:
        raise AzureDevOpsClientError(
            f"Error al descargar el adjunto {attachment_id} del work item "
            f"{work_item_id}: {str(e)}")


def register_tools(mcp) -> None:
    """
    Registra las herramientas de adjuntos de work items.
    
    Args:
        mcp: Instancia de MCP para registrar las herramientas
    """
    @mcp.tool()
    def download_work_item_attachment(
        work_item_id: int,
        attachment_id: str,
        output_path: str
    ) -> str:
        """
        Descarga un archivo adjunto de un elemento de trabajo.
        
        Use esta herramienta cuando necesite:
        - Descargar archivos adjuntos de work items
        - Guardar documentos o archivos relacionados con un work item
        - Obtener una copia local de los adjuntos para revisión
        
        Args:
            work_item_id: ID del elemento de trabajo
            attachment_id: ID del archivo adjunto
            output_path: Ruta donde guardar el archivo descargado
            
        Returns:
            Información sobre el archivo descargado incluyendo nombre, tamaño,
            tipo de contenido y ruta donde se guardó
        """
        try:
            wit_client = get_work_item_client()
            result = _download_attachment_impl(
                work_item_id, attachment_id, output_path, wit_client
            )
            
            # Formatear la respuesta
            response = [
                f"# Archivo adjunto descargado exitosamente",
                f"Nombre: {result['filename']}",
                f"Tamaño: {result['size']} bytes",
                f"Tipo de contenido: {result['content_type']}",
                f"Guardado en: {result['saved_to']}"
            ]
            
            return "\n".join(response)
        except AzureDevOpsClientError as e:
            return f"Error: {str(e)}" 