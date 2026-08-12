# Escenario CTF 02: Inyección de Mensajes GOOSE IEC 61850 (Estilo Industroyer2 / Ucrania 2022)

**Dificultad**: Media-Avanzada  
**Categoría**: Industrial Cybersecurity / OT Hacking / Substation Automation / IEC 61850  
**Autor**: CityLab Cyber Range  

---

## 1. Breve del Escenario (Storyline)

Durante una fase de pivoteo hacia la subestación eléctrica principal de la ciudad (`10.0.3.0/24`), un grupo de amenaza avanzado (APT) busca deshabilitar los interruptores de potencia sin pasar por el servidor SCADA central. 

Aprovechando la falta de autenticación y cifrado en el protocolo multicast **IEC 61850 GOOSE** (Generic Object Oriented Substation Events), el atacante inyecta frames ethernet/UDP falsificados con un número de estado (`stNum`) superior al del IED legítimo. Esto provoca la apertura inmediata de los disyuntores de la subestación y la desconexión del suministro eléctrico urbano.

---

## 2. Mapa de Componentes e IPs

- **Atacante (OT Cell / Pivoting)**: `10.0.3.99` (`h_attacker` o Jump host en zona OT)
- **Subestación Eléctrica IED**: `10.0.3.20` (`CITYLAB_IED1`)
- **Puerto UDP GOOSE**: `10102` (Multicast standard: `239.0.0.1`)
- **Controlador de Proceso**: `plc/iec61850_emulator.py`

---

## 3. Cadena de Ataque y Ejecución Paso a Paso

### Paso 1: Escaneo y Sniffing de Mensajes GOOSE
1. Capturar tráfico de la red OT para identificar la presencia de PDUs GOOSE:
   ```bash
   python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(('0.0.0.0', 10102)); print(s.recvfrom(1024))"
   ```
2. Extraer el identificador del IED (`gcb_ref`: `CITYLAB_IED1/LLN0$GO$gcb01`) y el `stNum` actual.

### Paso 2: Inyección de Disparo Falsificado (Spoofing)
1. Ejecutar el script de ataque `attacker/attack_goose_spoofing.py` forzando un `stNum` elevado y `breaker_pos = False` (TRIP):
   ```bash
   python3 attacker/attack_goose_spoofing.py --host 10.0.3.20 --port 10102 --ied CITYLAB_IED1 --stnum 500 --burst 5
   ```

### Paso 3: Verificación de Impacto Ciberfísico
1. Comprobar la apertura del interruptor en la telemetría del IED.
2. Observar la propagación de la caída de voltaje en la red eléctrica (`grid_voltage_pu -> 0.0`).

---

## 4. Detección y Regla SOC / SIEM (Blue Team)

El motor SIEM (`network/siem_pipeline.py`) detecta la anomalía al identificar saltos no secuenciales en `stNum` o discrepancias entre la MAC/IP origen y el registro estático del IED:

```json
{
  "event_category": "process_control",
  "event_type": "alert",
  "severity": "CRITICAL",
  "service_name": "iec61850_emulator",
  "message": "IEC 61850 GOOSE Anomaly Detected: Sequence Jump (stNum spoofing)"
}
```

---

## 5. Flags del Desafío CTF

- **FLAG 1 (GOOSE Sniffing)**: `FLAG_1{goose_pdu_multicast_sniffed_8812}`
- **FLAG 2 (Industroyer2 Substation Trip)**: `FLAG_2{industroyer2_goose_injection_success_9941}`
