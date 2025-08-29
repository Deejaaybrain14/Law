---
title: "MVP: Seguidor de Causas - Poder Judicial de Chile"
author: "Bea / Equipo"
date: "`r format(Sys.Date(), '%Y-%m-%d')`"

---


# Objetivo

Este documento describe y encapsula un **MVP** para un software que hace **seguimiento de causas del Poder Judicial de Chile**, con conectores a la **consulta pública** (sin login) y opción de ingesta de **notificaciones por correo** (IMAP). Incluye arquitectura, esquema de datos, y todo el código base para levantar el sistema con Docker.

> **Nota legal**: usa este software solo para las causas del estudio/cliente autorizadas y respetando condiciones de uso y tratamiento de datos personales. Evita automatizar flujos de autenticación estatal (p. ej. ClaveÚnica).
