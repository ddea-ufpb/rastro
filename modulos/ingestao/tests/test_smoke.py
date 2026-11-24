import rastro_ingestao


def test_pacote_importa() -> None:
    assert rastro_ingestao.__name__ == "rastro_ingestao"
    assert rastro_ingestao.__doc__
