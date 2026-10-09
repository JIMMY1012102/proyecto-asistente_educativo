# Asistente de Retroalimentación para Simulacros de Admisión — CNI

**Versión:** v1 — Semana 6
**Fecha:** 2026-10-09

## Diagrama de despliegue

```mermaid
flowchart TB
    subgraph MaquinaLaboratorio["Máquina del Laboratorio CNI\n(Windows / Linux)"]

        subgraph XAMPP["XAMPP"]

            subgraph ProcApache["Proceso Apache HTTP Server"]
                ApacheHTTP["Apache\nPuerto 80"]
                subgraph AppCI4["Aplicación PHP"]
                    CI4["CodeIgniter 4\n(PHP 8.x)\nRaíz pública: asistente_cni/public/"]
                end
                ApacheHTTP --> CI4
            end

            subgraph ProcMySQL["Proceso MySQL / MariaDB"]
                MySQLSrv["MySQL / MariaDB\nPuerto 3306"]
                subgraph EsquemaBD["Esquema"]
                    BDAsistente[("asistente_cni\nutf8mb4_unicode_ci\nInnoDB")]
                end
                MySQLSrv --> BDAsistente
            end

            subgraph phpMyAdmin["phpMyAdmin (gestión)"]
                PMA["phpMyAdmin\nPuerto 80 /phpmyadmin"]
            end

        end

        subgraph NavEstudiante["Navegador Estudiante"]
            NE["Chrome / Firefox"]
        end
        subgraph NavDocente["Navegador Docente"]
            ND["Chrome / Firefox"]
        end
        subgraph NavDireccion["Navegador Dirección"]
            NDi["Chrome / Firefox"]
        end

    end

    NE -- "HTTP :80" --> ApacheHTTP
    ND -- "HTTP :80" --> ApacheHTTP
    NDi -- "HTTP :80" --> ApacheHTTP
    CI4 -- "SQL (PDO)" --> MySQLSrv
    PMA -- "SQL" --> MySQLSrv
```
