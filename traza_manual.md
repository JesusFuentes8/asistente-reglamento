@'
# Traza a mano — Práctica 3

## E.1 La memoria (`max_mensajes = 4`)

Mensajes que se agregan: `u1`, `m1`, `u2`, `m2`, `u3`, `m3`, `u4` y `m4`.

| Llamada | Lista que recibe el modelo (predicción) | Cantidad | Lo que dio el programa | ¿Coincide? |
|---|---|---|---|---|
| 1 | [u1] | 1 | [u1] | Sí |
| 2 | [u1, m1, u2] | 3 | [u1, m1, u2] | Sí |
| 3 | [u2, m2, u3] | 3 | [u2, m2, u3] | Sí |
| 4 | [u3, m3, u4] | 3 | [u3, m3, u4] | Sí |

**Mensajes del historial completo al terminar:**  
8 mensajes en total: `[u1, m1, u2, m2, u3, m3, u4, m4]`.

**¿Qué recortes cambian por la regla «si el primero es del modelo, se descarta» y qué habría recibido el modelo sin ella?**  
Afecta a las llamadas 3 y 4. En la llamada 3, sin la regla se habrían enviado 4 mensajes: `[m1, u2, m2, u3]`; con la regla se descarta `m1` y quedan 3: `[u2, m2, u3]`. En la llamada 4, sin la regla se habrían enviado `[m2, u3, m3, u4]`; con la regla se descarta `m2` y quedan `[u3, m3, u4]`. Esto garantiza que el contexto comience siempre con el usuario.

**En el turno 4, «¿y eso a quién aplica?» se refiere a `u1`. ¿Lo puede entender el modelo? ¿Por qué?**  
No lo puede entender, porque en la llamada 4 el modelo únicamente recibe `[u3, m3, u4]`. El mensaje `u1` quedó fuera de la ventana de contexto de los últimos 4 mensajes y ya no forma parte del prompt enviado.

---

## E.2 Las citas

| Texto | `extraer_citas` (predicción) | Inválidas (predicción) | Lo que dio el programa | ¿Coincide? |
|---|---|---|---|---|
| T1 | ["9.II"] | [] | ["9.II"] | Sí |
| T2 | ["15", "8.VIII"] | [] | ["15", "8.VIII"] | Sí |
| T3 | ["7.XXV", "23"] | ["7.XXV", "23"] | ["7.XXV", "23"] | Sí |
| T4 | [] | [] | [] | Sí |
| T5 | ["14.3"] | [] | ["14.3"] | Sí |
| T6 | [] | [] | [] | Sí |

**¿Qué hace su código con T6? ¿Su verificación detecta el problema? ¿Qué parte del sistema debería evitar que el modelo escriba así?**  
En T6 (`Fundamento: Art. 7, fracciones XVIII y XXI`), la expresión regular busca el formato singular `fracc.` o `fracción` por cita individual. Como el texto agrupa dos fracciones con la palabra en plural («fracciones») y unidas por «y», la expresión regular no las reconoce y devuelve `[]`. El validador no detecta el problema porque no extrajo ninguna cita. Quien debe prevenir esta redacción es la instrucción del sistema en `prompts/sistema.md`, obligando al modelo a citar cada fracción por separado con el formato exacto `Art. N, fracc. R` separadas por punto y coma.

---

## E.3 Los tokens de la conversación C1

| Turno | Mensajes enviados | Tokens de entrada | Tokens de salida |
|---|---|---|---|
| C1-1 | 1 | 6548 | 142 |
| C1-2 | 3 | 6692 | 118 |
| C1-3 | 3 | 6780 | 125 |

**¿Por qué crecen los tokens de entrada? ¿Qué parte de ellos es el Reglamento?**  
Crecen porque se van sumando las preguntas y respuestas de los turnos previos que entran en la ventana de memoria corta. La mayor parte de los tokens de entrada (aproximadamente 6,450 tokens) corresponde al texto completo del Reglamento que se inyecta en cada llamada dentro de la instrucción de sistema.

**¿Qué pasaría en el turno 10 de una conversación larga si `recortar` no existiera?**  
El historial enviaría los 19 mensajes previos acumulados. Los tokens de entrada crecerían de forma continua en cada turno, incrementando la latencia, el costo por llamada y el riesgo de agotar la cuota de tokens por minuto (TPM) permitida por la API.
