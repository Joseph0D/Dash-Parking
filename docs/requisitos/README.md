# Requisitos — Dash Parking

Este directorio reúne las historias de usuario (HU), requisitos funcionales (RF), requisitos
no funcionales (RNF) y restricciones del proyecto. La relación entre ellos es de muchos a muchos:
una HU puede necesitar varios RF y un RF puede soportar varias HUs. No se asume una relación 1:1.

## Historias de Usuario ([`HUs/`](HUs/))

Hay 42 historias existentes (HU-01 a HU-31, incluidas sus subdivisiones) y seis historias
nuevas (HU-32 a HU-37) para dueño, gestión aislada, recuperación de contraseña y los dos flujos
QR diferenciados.
El estado y la decisión de cada historia se encuentran en la
[matriz de revisión y trazabilidad](matriz-trazabilidad.md).

## Requisitos Funcionales ([`RFs/`](RFs/))

RF-001 a RF-017 conservan los flujos operativos y de pago originales, con las modificaciones
indicadas en la matriz. RF-018 a RF-025 documentan perfil y vehículos, operación del dueño,
recuperación por correo, descubrimiento geográfico, QR por vehículo, historial de pagos y
notificaciones.

## Requisitos No Funcionales ([`RNFs/`](RNFs/))

| RNF | Categoría |
|---|---|
| [RNF-001](RNFs/RNF-001_seguridad.md) | Seguridad y control de acceso |
| [RNF-002](RNFs/RNF-002_rendimiento_disponibilidad.md) | Rendimiento y disponibilidad |
| [RNF-003](RNFs/RNF-003_usabilidad.md) | Usabilidad, incluida la experiencia móvil |
| [RNF-004](RNFs/RNF-004_integridad_y_confiabilidad.md) | Integridad y confiabilidad |
| [RNF-005](RNFs/RNF-005_mantenibilidad_y_escalabilidad.md) | Mantenibilidad, pruebas y trazabilidad |
| [RNF-006](RNFs/RNF-006_compatibilidad.md) | Compatibilidad y portabilidad |
| [RNF-007](RNFs/RNF-007_privacidad.md) | Privacidad y protección de datos personales |
| [RNF-008](RNFs/RNF-008_despliegue_publico.md) | Despliegue y operación pública |

## Mapa de cambios y trazabilidad

La [matriz de revisión y trazabilidad](matriz-trazabilidad.md) clasifica cada HU/RF/RNF como
mantener, modificar, retirar como elemento independiente o agregar; relaciona historias,
requisitos, módulos de código y pruebas, y distingue lo implementado de lo pendiente.

## Restricciones

[`restricciones.md`](restricciones.md) registra las decisiones tecnológicas, de seguridad y de
operación que deben respetarse durante las siguientes fases.
