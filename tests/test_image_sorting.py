import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from services.image_service import chave_ordenacao_natural


class MockUploadedFile:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"MockUploadedFile('{self.name}')"


def test_natural_sort_numbers_sequence():
    """Testa se 2 vem antes de 10 na ordenação natural."""
    nomes = [
        "Foto 10.jpg",
        "Foto 2.jpg",
        "Foto 1.jpg",
        "Foto 20.jpg",
        "Foto 3.jpg",
        "Foto 100.jpg"
    ]
    ordenados = sorted(nomes, key=chave_ordenacao_natural)
    esperado = [
        "Foto 1.jpg",
        "Foto 2.jpg",
        "Foto 3.jpg",
        "Foto 10.jpg",
        "Foto 20.jpg",
        "Foto 100.jpg"
    ]
    assert ordenados == esperado


def test_natural_sort_uploaded_file_objects():
    """Testa se objetos com atributo .name (como UploadedFile) são ordenados corretamente."""
    files = [
        MockUploadedFile("IMG_10.jpg"),
        MockUploadedFile("IMG_2.jpg"),
        MockUploadedFile("IMG_1.jpg"),
        MockUploadedFile("IMG_20.jpg"),
    ]
    ordenados = sorted(files, key=chave_ordenacao_natural)
    nomes_ordenados = [f.name for f in ordenados]
    assert nomes_ordenados == ["IMG_1.jpg", "IMG_2.jpg", "IMG_10.jpg", "IMG_20.jpg"]


def test_natural_sort_reverse():
    """Testa a ordenação reversa (Z-A / 9-0)."""
    files = [
        MockUploadedFile("Registro 1.png"),
        MockUploadedFile("Registro 10.png"),
        MockUploadedFile("Registro 2.png"),
    ]
    ordenados_desc = sorted(files, key=chave_ordenacao_natural, reverse=True)
    nomes_ordenados = [f.name for f in ordenados_desc]
    assert nomes_ordenados == ["Registro 10.png", "Registro 2.png", "Registro 1.png"]


def test_natural_sort_parentheses_and_prefixes():
    """Testa arquivos nomeados com parênteses do Windows Explorer como Foto (1).jpg."""
    nomes = [
        "Vistoria (10).jpg",
        "Vistoria (1).jpg",
        "Vistoria (2).jpg",
        "Vistoria (20).jpg",
    ]
    ordenados = sorted(nomes, key=chave_ordenacao_natural)
    assert ordenados == [
        "Vistoria (1).jpg",
        "Vistoria (2).jpg",
        "Vistoria (10).jpg",
        "Vistoria (20).jpg",
    ]


def test_natural_sort_case_and_accent_insensitive():
    """Testa se a ordenação lida com acentos e maiúsculas/minúsculas sem quebrar."""
    nomes = [
        "área 2.jpg",
        "Área 10.jpg",
        "Area 1.jpg",
    ]
    ordenados = sorted(nomes, key=chave_ordenacao_natural)
    # Area 1 deve vir antes de área 2 e Área 10
    assert ordenados[0] in ["Area 1.jpg", "área 1.jpg"]
    assert ordenados[1] == "área 2.jpg"
    assert ordenados[2] == "Área 10.jpg"


def test_preservation_of_upload_order():
    """Testa que quando 'Ordem de Upload' é mantida, a lista original não é modificada."""
    upload_sequence = [
        MockUploadedFile("Foto 10.jpg"),
        MockUploadedFile("Foto 1.jpg"),
        MockUploadedFile("Foto 20.jpg"),
        MockUploadedFile("Foto 2.jpg"),
    ]
    # Simulação da lógica em app.py para 'Ordem de Upload'
    photos_to_sort = list(upload_sequence)
    sort_option = "Ordem de Upload"
    if sort_option == "Nome (A-Z / 0-9)":
        photos_to_sort.sort(key=chave_ordenacao_natural)
    elif sort_option == "Nome (Z-A / 9-0)":
        photos_to_sort.sort(key=chave_ordenacao_natural, reverse=True)

    assert [p.name for p in photos_to_sort] == [
        "Foto 10.jpg",
        "Foto 1.jpg",
        "Foto 20.jpg",
        "Foto 2.jpg",
    ]


def test_carousel_index_retention_on_reorder():
    """Testa que a foto selecionada no carrossel mantém o foco após reordenação."""
    files = [
        MockUploadedFile("Foto 10.jpg"),
        MockUploadedFile("Foto 2.jpg"),
        MockUploadedFile("Foto 1.jpg"),
    ]
    # Usuário estava vendo 'Foto 2.jpg' no índice 1 da lista não ordenada
    foto_ativa_anterior = files[1].name  # 'Foto 2.jpg'
    
    # Reordena para A-Z
    photos_to_sort = list(files)
    photos_to_sort.sort(key=chave_ordenacao_natural)
    # Nova ordem: Foto 1.jpg (0), Foto 2.jpg (1), Foto 10.jpg (2)
    
    new_carousel_index = None
    for new_idx, photo in enumerate(photos_to_sort):
        if photo.name == foto_ativa_anterior:
            new_carousel_index = new_idx
            break
            
    assert new_carousel_index == 1
    assert photos_to_sort[new_carousel_index].name == "Foto 2.jpg"
