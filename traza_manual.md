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
 `[u1, m1, u2, m2, u3, m3, u4, m4]`.

**¿Qué recortes cambian por la regla "si el primero es del modelo, se descarta" y qué habría recibido el modelo sin ella?**  
Afecta en las llamadas 3 y 4:
 En la 3, sin la regla se mandarían 4 mensajes: `[m1, u2, m2, u3]`. Como empieza con respuesta del bot (`m1`), se descarta y quedan 3: `[u2, m2, u3]`.
 En la 4 pasa lo mismo: sin la regla entrarían `[m2, u3, m3, u4]`, pero se quita `m2` y solo se envían 3: `[u3, m3, u4]`.  
Esto garantiza que la conversación enviada al modelo siempre empiece con un mensaje del usuario.

**En el turno 4, «¿y eso a quién aplica?» se refiere a `u1`. ¿Lo puede entender el modelo? ¿Por qué?**  
No, no hay forma de que lo entienda. En la llamada 4 el modelo solo recibe `[u3, m3, u4]`. El mensaje `u1` ya se quedó fuera de la ventana por el recorte de memoria, así que ya no existe dentro del contexto que se le manda.

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
En T6 (`Fundamento: Art. 7, fracciones XVIII y XXI`), la regex no agarra nada porque está programada para buscar palabras en singular (`fracc.` o `fracción`) por cada cita. Al venir en plural ("fracciones") y separadas con "y", la regex se las salta y regresa la lista vacía `[]`. Por eso mismo el validador ni se entera de que hubo detalles, ya que no extrajo nada para comparar.  
Esto se tiene que prevenir desde el prompt del sistema (`prompts/sistema.md`), poniéndole la regla estricta al modelo de que siempre cite cada fracción por separado con el formato exacto `Art. N, fracc. R` y usando punto y coma entre ellas.

---

## E.3 Los tokens de la conversación C1

| Turno | Mensajes enviados | Tokens de entrada | Tokens de salida |
|---|---|---|---|
| C1-1 | 1 | 6548 | 142 |
| C1-2 | 3 | 6692 | 118 |
| C1-3 | 3 | 6780 | 125 |

**¿Por qué crecen los tokens de entrada? ¿Qué parte de ellos es el Reglamento?**  
Van subiendo porque en cada turno se van acumulando las preguntas y respuestas anteriores que entran en la memoria corta. Aun así, casi todos los tokens de entrada (unos 6,450) se van en el texto completo del reglamento que le metemos en el system prompt en cada llamada.

**¿Qué pasaría en el turno 10 de una conversación larga si `recortar` no existiera?**  
El historial mandaría de golpe los 19 mensajes acumulados. Los tokens de entrada crecerían sin parar en cada turno, lo que haría las respuestas mucho más lentas, gastaría tokens y nos arriesgaría a toparnos con el límite de cuota (TPM) de la API.