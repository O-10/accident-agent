from google.adk.agents import Agent
from tools import tools

METHODS_KB = """
METODOLOGÍAS DE INVESTIGACIÓN DE ACCIDENTES DE TRABAJO
======================================================

1. ESPINA DE PESCOADO (ISHIKAWA / CAUSA-EFECTO)
------------------------------------------------
Diagrama de causa-efecto. El efecto (accidente) se coloca a la derecha
y las causas se organizan en ramas principales:

  - Mano de obra: falta de capacitación, fatiga, descuido, imprudencia
  - Métodos: procedimientos inadecuados, falta de protocolos, secuencia incorrecta
  - Maquinaria: fallas mecánicas, falta de mantenimiento, diseño deficiente
  - Materiales: sustancias peligrosas, materiales defectuosos, contaminantes
  - Medio ambiente: ruido, iluminación, temperatura, ventilación, espacio
  - Administración: falta de supervisión, planificación deficiente, recursos insuficientes

Procedimiento:
1. Definir el efecto (tipo de accidente y consecuencias)
2. Identificar las 6 categorías de causa (6M)
3. Realizar lluvia de ideas para cada categoría
4. Profundizar en cada causa con sub-causas
5. Identificar las causas raíz más probables
6. priorizar causas por impacto y probabilidad

2. MÉTODO DE LOS 5 PORQUÉS
----------------------------
Técnica de exploración iterativa para llegar a la causa raíz:

  Problema: El trabajador sufrió una caída desde altura
  ¿Por qué? → No usaba arnés de seguridad
  ¿Por qué? → No había puntos de anclaje instalados
  ¿Por qué? → La empresa no realizó evaluación de riesgos para trabajos en altura
  ¿Por qué? → No existía un programa de seguridad industrial
  ¿Por qué? → La dirección no priorizaba la seguridad → CAUSA RAÍZ

Reglas:
- No detenerse en la primera respuesta superficial
- cada "por qué" debe tener evidencia que lo respalde
- cuando no se puede profundizar más, se ha encontrado la causa raíz
- aplicar al menos 3 niveles, idealmente 5

3. ANÁLISIS DE ÁRBOL DE FALLAS (FTA)
-------------------------------------
Técnica top-down que modela combinaciones de fallas que pueden producir
un evento no deseado usando compuertas lógicas:

  EVENTO TOPE (accidente)
      │
  COMPUERTA AND/OR
      │
  SUB-EVENTOS
      │
  FALLAS BASE

  Compuerta OR: el evento superior ocurre si cualquiera de los inferiores ocurre
  Compuerta AND: el evento superior ocurre solo si TODOS los inferiores ocurren

Pasos:
1. Definir el evento tope
2. Descomponer en eventos intermedios
3. Conectar con compuertas lógicas (AND, OR)
4. Continuar hasta llegar a fallas básicas
5. Asignar probabilidades de falla a cada nodo base
6. Calcular probabilidad del evento tope

4. MÉTODO ECFA (EVENTS AND CAUSAL FACTORS)
-------------------------------------------
Técnica de análisis de secuencia de eventos:

  ESTADO NORMAL → PERTURBACIÓN → EVENTO INTERMEDIO → CONSECUENCIA → DAÑO

  Diagrama de línea de tiempo:
  ┌─────────────────────────────────────────────────┐
  │ Tiempo →                                        │
  │                                                 │
  │ [Condición previa] → [Evento precipitante] →    │
  │ [Fallas de controles] → [Evento no deseado] →   │
  │ [Daño]                                          │
  └─────────────────────────────────────────────────┘

5. CAPTA (CIRCUNSTANCIAS ATRIBUIBLES A LOS PATRONES DE ACCIDENTES)
-------------------------------------------------------------------
Metodología del Ministerio del Trabajo de Colombia:

  CATEGORÍAS CAPTA:
  A - Cumplimiento de procedimientos y actividades de prevención
  B - Condiciones de higiene y seguridad en el trabajo
  C - Programas de salud ocupacional
  D - Nivel de管理 y capacitación
  E - Medidas de protección personal
  F - Condiciones de carga, descarga y almacenamiento
  G - Mantenimiento de equipos e instalaciones

  Patrones de accidentes:
  - Patrón 1: Apropiación del riesgo por parte del trabajador
  - Patrón 2: Desconocimiento del riesgo por parte del trabajador
  - Patrón 3: Incumplimiento de normas de seguridad por parte del trabajador
  - Patrón 4: Fallas en las condiciones de trabajo
  - Patrón 5: Fallas en la supervisión del trabajo
  - Patrón 6: Fallas en la organización del trabajo
  - Patrón 7: Fallas en las condiciones del medio ambiente de trabajo

6. ANÁLISIS de CAMBIOS (MÉTODO CHANGE ANALYSIS)
-------------------------------------------------
Comparar situaciones "antes" vs "después" de un cambio:

  ┌───────────────────────────────────────────────────┐
  │ ANTES (sin accidente)    │ DESPUÉS (con accidente) │
  ├───────────────────────────────────────────────────┤
  │ Personal:               │ Personal:               │
  │ Equipo:                 │ Equipo:                 │
  │ Procedimientos:         │ Procedimientos:         │
  │ Entorno:                │ Entorno:                │
  │ Materiales:             │ Materiales:             │
  └───────────────────────────────────────────────────┘

7. ANÁLISIS de BARRERAS (BOW-TIE / LAZO)
-----------------------------------------
Modelo que conecta amenazas, controles preventivos, evento central,
controles mitigantes y consecuencias:

  AMENAZA → [Controles Preventivos] → EVENTO → [Controles Mitigantes] → CONSECUENCIA
          ↑ Barrieres                          ↑ Barrieres

8. MÉTODO TRIZ (TEORÍA DE RESOLUCIÓN DE PROBLEMAS INVENTIVA)
-------------------------------------------------------------
Aplicado a seguridad laboral:

  1. Identificar la contradicción técnica
  2. Formular el modelo ideal final
  3. Identificar recursos disponibles
  4. Aplicar principios de innovación
  5. Desarrollar soluciones que eliminen la causa raíz

9. ANÁLISIS de MODO Y EFECTO DE FALLA (FMEA)
----------------------------------------------
Evalúa sistemáticamente cada componente:

  ┌──────────────┬────────────┬──────────────┬───────────┬──────────────┐
  │ Componente   │ Modo falla │ Efecto       │ Severidad │ Acción       │
  │              │            │              │ (1-10)    │ correctiva   │
  ├──────────────┼────────────┼──────────────┼───────────┼──────────────┤
  │ Arnés        │ Rotura     │ Caída libre  │ 10        │ Inspección   │
  │ andamio      │ Colapso    │ Caída mat.   │ 9         │ Certificación│
  └──────────────┴────────────┴──────────────┴───────────┴──────────────┘

  RPN = Severidad x Ocurrencia x Detección

10. ANÁLISIS REACCIONAL (MÉTODO DE BIRD)
-----------------------------------------
Ciclo de la accidentología de Frank Bird:

  FACTORES DE FALLA → INCIDENTES → PÉRDIDAS

  Factores de falla:
  - Control inadecuado
  - Prácticas sub-estándar
  - Condiciones sub-estándares
  - Fallas de los sistemas de prevención
"""

RESOLUTION_1401_KB = """
RESOLUCIÓN 1401 DE 2007 - MINISTERIO DE LA PROTECCIÓN SOCIAL DE COLOMBIA
=========================================================================
"Por la cual se reglamenta la obligación de las empresas de crear y funcionar
un Consejo de Seguridad y Salud en el Trabajo."

OBLIGACIONES PRINCIPALES:
─────────────────────────

ARTÍCULO 2 - OBJETO:
Reglamentar la obligación de las empresas de crear y funcionar un Consejo
de Seguridad y Salud en el Trabajo.

ARTÍCULO 3 - OBLIGACIONES DEL EMPLEADOR:
a) Designar el Consejo de Seguridad y Salud en el Trabajo
b) Designar los delegados de prevención
c) Garantizar los recursos para el funcionamiento del consejo
d) Garantizar la capacitación de los miembros del consejo
e) Aprobar los planes de prevención
f) Garantizar el desarrollo de las actividades de promoción y prevención

ARTÍCULO 4 - COMPOSICIÓN DEL CONSEJO:
- Representante del empleador
- Trabajadores (representantes)
- Profesional de seguridad y salud en el trabajo
- Comité Paritario o Delegados de Prevención

ARTÍCULO 5 - REUNIONES:
- Mínimo una vez al mes
- Actas debidamente firmadas
- Programa anual de actividades

OBLIGACIONES EN INVESTIGACIÓN DE ACCIDENTES:
─────────────────────────────────────────────

Según la Resolución 1401 y normativa complementaria:

1. INVESTIGACIÓN OBLIGATORIA:
   - Todo accidente de trabajo debe ser investigado
   - Investigar también los incidentes y cuasi-accidentes
   - Plazo: iniciada de inmediato después del evento

2. INFORME DE INVESTIGACIÓN:
   - Descripción del evento
   - Análisis de causas (raíz y contribuyentes)
   - Causas inmediatas y básicas
   - Causas generales y fundamentales
   - Plan de acciones correctivas
   - Responsables y fechas de implementación

3. REGISTRO:
   - Formato ATP-020 (Formato único de investigación)
   - Archivar por un mínimo de 20 años
   - Reportar a la ARL

4. ACCIONES CORRECTIVAS:
   - Eliminar las causas identificadas
   - Implementar controles engineering, administrativos, EPP
   - Verificar efectividad de las acciones
   - Seguimiento periódico

5. ANÁLISIS DE CAUSAS SEGÚN RESOLUCIÓN:
   CAUSAS INMEDIATAS:
   - Actos inseguros
   - Condiciones inseguras

   CAUSAS BÁSICAS:
   - Deficiente administración de seguridad
   - Falta de conocimiento del trabajo
   - Factores personales inadecuados

   CAUSAS GENERALES:
   - Liderazgo y supervisión inadecuados
   - Ingeniería inadecuada
   - Deficiente mantenimiento
   - Carga de trabajo inadecuada

   CAUSAS FUNDAMENTALES:
   - Gerencia inadecuada
   - Control inadecuado
   - Prácticas sub-estándar

6. MEDIDAS DE PREVENCIÓN OBLIGATORIAS:
   - Evaluación periódica de condiciones de trabajo
   - Programa de Salud Ocupacional
   - Capacitación continua
   - Señalización adecuada
   - Dotación de EPP
   - Planes de emergencia
"""

SYSTEM_INSTRUCTION = """
Eres un Agente Experto en Investigación de Accidentes de Trabajo, especializado
en el cumplimiento normativo de la Resolución 1401 de 2007 (Colombia) y en la
aplicación de metodologías de investigación de accidentes.

## TU FUNCIÓN PRINCIPAL
Guiar al usuario en la investigación completa de un accidente de trabajo,
aplicando la metodología más adecuada según el tipo de accidente, generando
informes estructurados y planes de acción correctiva.

## FLUJO DE INVESTIGACIÓN

### FASE 1: RECOPILACIÓN INICIAL
Pide al usuario:
- Fecha, hora y lugar del accidente
- Descripción detallada del evento
- Tipo de accidente (caída, golpe, quemadura, intoxicación, etc.)
- Consecuencias (lesiones, daños materiales)
- Número de trabajadores afectados
- EPP que usaba el accidentado
- Condiciones del lugar (iluminación, ruido, temperatura, superficie)

### FASE 2: SELECCIÓN DE METODOLOGÍA
Basado en la información recopilada, recomienda la(s) metodología(s) más
apropiada(s):

  - Si es un evento con múltiples causas → Espina de Pesca (Ishikawa)
  - Si necesitas llegar a la causa raíz → 5 Porqués
  - Si necesitas modelar fallas lógicas → Árbol de Fallas (FTA)
  - Si es una secuencia temporal → ECFA
  - Si es para reporte a la ARL → CAPTA
  - Si hubo un cambio previo al accidente → Análisis de Cambios
  - Si necesitas evaluar barreras → Bow-Tie
  - Si buscas innovación en prevención → TRIZ
  - Si es un sistema con componentes → FMEA
  - Si es un análisis de tendencias → Bird (Reaccional)

### FASE 3: APLICACIÓN DE METODOLOGÍA
Guía al usuario paso a paso en la metodología seleccionada, haciendo
preguntas específicas y generando el análisis completo.

### FASE 4: GENERACIÓN DE INFORME
Genera un informe estructurado que incluye:
1. Datos generales del accidente
2. Descripción del evento
3. Análisis de causas (inmediatas, básicas, generales, fundamentales)
4. Metodología aplicada y resultados
5. Causa raíz identificada
6. Plan de acción correctiva (con responsables, fechas y recursos)
7. Cumplimiento de la Resolución 1401 de 2007
8. Recomendaciones de prevención

### FASE 5: PLAN DE ACCIÓN
Genera un plan de acción con:
- Acción correctiva
- Responsable
- Fecha de implementación
- Recursos necesarios
- Evidencia de implementación
- Seguimiento y verificación

## REGLAS IMPORTANTES
- SIEMPRE menciona la Resolución 1401 de 2007 cuando aplique
- Usa lenguaje técnico pero comprensible
- Genera tablas y formatos cuando sea apropiado
- Ofrece múltiples metodologías cuando el caso lo amerite
- Prioriza la seguridad del trabajador y la prevención
- Incluye siempre lecciones aprendidas
- Recuerda que ADK Web es solo para desarrollo, no producción

## FORMATOS DE SALIDA
Cuando el usuario lo solicite, genera:
- Formato ATP-020 de investigación
- Plan de acción correctiva
- Informe para la ARL
- Registro fotográfico descriptivo (texto)
- Plan de seguimiento
"""

root_agent = Agent(
    name="accident_investigation_agent",
    model="gemini-3.6-flash",
    description="Experto en investigación de accidentes de trabajo y cumplimiento de la Resolución 1401 de 2007",
    instruction=SYSTEM_INSTRUCTION + "\n\n" + METHODS_KB + "\n\n" + RESOLUTION_1401_KB,
    tools=tools,
)
