import rastro_consulta


def test_pacote_importa() -> None:
    assert rastro_consulta.__name__ == "rastro_consulta"
    assert rastro_consulta.__doc__
