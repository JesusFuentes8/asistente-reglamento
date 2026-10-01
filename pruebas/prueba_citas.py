"""Suite de pruebas locales sin red."""
from app.reglamento import cargar_reglamento, indice_citas, texto_para_prompt
from app.memoria import agregar, recortar
from app.citas import extraer_citas, validar_citas
from app.bot import leer_permitidos, partir_mensaje, usuario_anonimo


def ejecutar_pruebas():
    reg = cargar_reglamento("data/reglamento_estudiantes_tecnm.json")
    indice = indice_citas(reg)
    assert len(indice) == 126, f"Índice esperado: 126, obtenido: {len(indice)}"

    texto_p = texto_para_prompt(reg)
    assert "REGLAMENTO DE ESTUDIANTES DEL TECNOLÓGICO NACIONAL DE MÉXICO" in texto_p
    assert "Art. 9, fracc. II." in texto_p
    assert "PRIMERO." in texto_p

    assert extraer_citas("Fundamento: Art. 9, fracc. II") == ["9.II"]
    assert extraer_citas("según el artículo 15 y el Art. 8 fracción VIII") == ["15", "8.VIII"]
    assert extraer_citas("Fundamento: Art. 7, fracc. XXV; Art. 23") == ["7.XXV", "23"]
    assert extraer_citas("Fundamento: no consta en el Reglamento de Estudiantes") == []
    assert extraer_citas("Art. 14, numeral 3; art. 14, numeral 3") == ["14.3"]

    v = validar_citas(["9.II", "31.II", "15"], indice)
    assert v["validas"] == ["9.II", "15"]
    assert v["invalidas"] == ["31.II"]

    hist = []
    agregar(hist, "usuario", "hola")
    agregar(hist, "modelo", "buen dia")
    assert len(hist) == 2
    assert recortar(hist, 0) == []

    hist_4 = [
        {"rol": "usuario", "texto": "u1"},
        {"rol": "modelo", "texto": "m1"},
        {"rol": "usuario", "texto": "u2"},
        {"rol": "modelo", "texto": "m2"},
        {"rol": "usuario", "texto": "u3"},
    ]
    rec = recortar(hist_4, 4)
    assert len(rec) == 3
    assert rec[0]["texto"] == "u2"

    assert leer_permitidos("123, 456,789") == {123, 456, 789}
    assert leer_permitidos("") == set()

    partes = partir_mensaje("hola mundo", limite=5)
    assert partes == ["hola", "mundo"]

    u_anon = usuario_anonimo(123456789)
    assert len(u_anon) == 10
    assert isinstance(u_anon, str)

    orig = [{"rol": "usuario", "texto": "1"}]
    _ = recortar(orig, 1)
    assert len(orig) == 1

    print("OK: Todas las pruebas pasaron exitosamente.")


if __name__ == "__main__":
    ejecutar_pruebas()