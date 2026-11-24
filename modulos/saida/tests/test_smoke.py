import rastro_saida


def test_pacote_importa() -> None:
    assert rastro_saida.__name__ == "rastro_saida"
    assert rastro_saida.__doc__
