# Asistente de Retroalimentación para Simulacros de Admisión — CNI

**Versión:** v1 — Semana 6
**Fecha:** 2026-10-09

## C4 Nivel 2 — Contenedores

```mermaid
flowchart TB
    subgraph MaquinaLaboratorio["Máquina del Laboratorio CNI"]

        subgraph XAMPP["XAMPP"]

            subgraph ServidorApache["Servidor Apache"]
                AplicacionWeb["Aplicación Web\n(CodeIgniter 4 / PHP 8.x)\nasistente_cni/public/"]
            end

            subgraph ServidorBD["Servidor MySQL / MariaDB"]
                BaseDatos[("Base de Datos\nasistente_cni\n(datos simulados)")]
            end

        end

        subgraph ClienteWeb["Cliente Web"]
            Navegador["Navegador\n(Estudiante / Docente / Dirección)"]
        end

    end

    Navegador -- "HTTP · Peticiones de página y formularios" --> AplicacionWeb
    AplicacionWeb -- "Consultas SQL de solo lectura\n(SELECT)" --> BaseDatos
    BaseDatos -- "Conjuntos de resultados" --> AplicacionWeb
    AplicacionWeb -- "HTML renderizado" --> Navegador
```
