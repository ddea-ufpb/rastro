import rastro_nucleo


def test_pacote_importa() -> None:
    assert rastro_nucleo.__name__ == "rastro_nucleo"
    assert rastro_nucleo.__doc__
