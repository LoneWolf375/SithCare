import re

def validar_formato_rut(rut):
    # Acepta 7 u 8 dígitos, guión, y dígito verificador (numérico o K/k)
    return bool(re.fullmatch(r'\d{7,8}-[\dkK]', rut))