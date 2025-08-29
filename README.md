---
title: "MVP: Seguidor de Causas - Poder Judicial de Chile"
author: "Bea / Equipo"
date: "`r format(Sys.Date(), '%Y-%m-%d')`"
output:
  html_document:
    toc: true
    toc_depth: 3
    toc_float: true
    number_sections: true
    code_folding: hide
  pdf_document: default
fontsize: 11pt
lang: es
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE)
```

# Objetivo

Este documento describe y encapsula un **MVP** para un software que hace **seguimiento de causas del Poder Judicial de Chile**, con conectores a la **consulta pública** (sin login) y opción de ingesta de **notificaciones por correo** (IMAP). Incluye arquitectura, esquema de datos, y todo el código base para levantar el sistema con Docker.

> **Nota legal**: usa este software solo para las causas del estudio/cliente autorizadas y respetando condiciones de uso y tratamiento de datos personales. Evita automatizar flujos de autenticación estatal (p. ej. ClaveÚnica).
