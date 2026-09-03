#!/usr/bin/env python3
"""helics_sim/sentinel_utils.py — Funciones canónicas de sanitización de centinelas HELICS Core.

HELICS Core retorna INT64_MIN (-9223372036854775808) o HELICS_BIG_NUMBER (-9.99e48) cuando
una suscripción no ha sido publicada aún por otro federado o se encuentra pre-inicializada.
Este módulo provee funciones puras y deterministas para normalizar estas señales en producción.
"""
from typing import Optional


def sanitize_trip_signal(raw_value: int) -> int:
    """Sanitiza señales booleanas/enteras de disparo (trip/interlock/ups).
    
    Solo un valor exactamente igual a 1 representa un disparo o activación legítima.
    Cualquier valor no inicializado (INT64_MIN = -9223372036854775808 o valores centinela < -9000000)
    se normaliza estrictamente a 0.
    """
    return 1 if raw_value == 1 else 0


def sanitize_telemetry_double(
    raw_value: float,
    default: float = 0.0,
    min_val: float = 0.0,
    max_val: Optional[float] = None,
) -> float:
    """Sanitiza valores analógicos continuos tipo double.
    
    Si el valor es inferior al umbral de centinela HELICS (-1e20) o excede un rango admisible
    (ej. frecuencia eléctrica fuera de límites físicos > 70 Hz durante inicialización),
    se reemplaza por el valor por defecto configurado. En caso contrario, se acota al valor mínimo admisible.
    """
    if raw_value < -1e20:
        return default
    if max_val is not None and raw_value > max_val:
        return default
    return max(min_val, raw_value)
