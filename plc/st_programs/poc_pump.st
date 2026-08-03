(*
poc_pump.st - Programa Structured Text para PoC
Descripcion:
 - Control simple de una bomba (pump) con arranque seguro (TON) y parada retardada (TON)
 - Variables mapeables vía OpenPLC/Modbus (coil mapping sugerido):
     coil 0 -> pump_start (BOOL)  ; comando de arranque
     coil 1 -> pump_stop  (BOOL)  ; comando de parada
     coil 2 -> pump_running (BOOL) ; estado de la bomba (salida)
     coil 3 -> pump_fault (BOOL)   ; indicador de fallo (salida)

Nota: El mapeo de coils se configura en OpenPLC Runtime. El programa usa temporizadores
TON estándar IEC61131-3. Mantener simple y seguro para pruebas de compromiso.
*)

PROGRAM POC_PUMP
VAR
    pump_start     : BOOL := FALSE;    (* Entrada: comando de arranque *)
    pump_stop      : BOOL := FALSE;    (* Entrada: comando de parada  *)
    pump_running   : BOOL := FALSE;    (* Salida: estado de la bomba   *)
    pump_fault     : BOOL := FALSE;    (* Salida: indicador de fallo  *)

    start_timer    : TON;              (* Temporizador on-delay para arranque seguro *)
    stop_timer     : TON;              (* Temporizador on-delay para parada segura  *)
END_VAR

(* Configuración de temporizadores: 5s para arranque, 3s para parada *)
start_timer(IN := pump_start AND NOT pump_running, PT := T#5S);
stop_timer(IN := pump_stop AND pump_running, PT := T#3S);

(* Lógica principal: *)
IF start_timer.Q THEN
    pump_running := TRUE;
ELSIF stop_timer.Q THEN
    pump_running := FALSE;
END_IF;

(* Condición de fallo simple: start y stop simultáneos -> fault *)
pump_fault := pump_start AND pump_stop;

END_PROGRAM
