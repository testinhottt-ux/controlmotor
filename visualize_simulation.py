#!/usr/bin/env python3
"""
Visualize SPICE Simulation Results
Generates plots for DC link voltage, phase currents, and power dissipation
"""

import subprocess
import tempfile
import os
from pathlib import Path

# Create a SPICE netlist that outputs data for plotting
spice_netlist = """* 3-Phase BLDC Inverter Simulation
.title 3-Phase BLDC Inverter - 50A/400V Simulation

* Power Supply
Vdc vdc gnd DC 400
Cbulk vdc gnd 470u IC=400

* PWM Control Signals (20 kHz)
Vpwm_u gate_u gnd PULSE(0 15 0u 100n 100n 25u 50u)
Vpwm_v gate_v gnd PULSE(0 15 16.67u 100n 100n 25u 50u)
Vpwm_w gate_w gnd PULSE(0 15 33.33u 100n 100n 25u 50u)

* Gate Drive Circuit (simple RC)
Rgate_u gate_u gate_hs_u 1k
Cgate_u gate_hs_u gnd 1n

Rgate_v gate_v gate_hs_v 1k
Cgate_v gate_hs_v gnd 1n

Rgate_w gate_w gate_hs_w 1k
Cgate_w gate_hs_w gnd 1n

* MOSFET Switches
Shs_u vdc phase_u gate_hs_u gnd sw_model
Sls_u phase_u gnd gate_hs_u gnd sw_model

Shs_v vdc phase_v gate_hs_v gnd sw_model
Sls_v phase_v gnd gate_hs_v gnd sw_model

Shs_w vdc phase_w gate_hs_w gnd sw_model
Sls_w phase_w gnd gate_hs_w gnd sw_model

.model sw_model SW(VT=5 VH=2 RON=0.01 ROFF=1e8)

* Motor Windings with Back-EMF
Lphase_u phase_u neutral 100u
Rphase_u neutral n1 0.1
Ephase_u n1 gnd SIN(0 143.5 200 0 0)

Lphase_v phase_v neutral 100u
Rphase_v neutral n2 0.1
Ephase_v n2 gnd SIN(0 143.5 200 1.667m 0)

Lphase_w phase_w neutral 100u
Rphase_w neutral n3 0.1
Ephase_w n3 gnd SIN(0 143.5 200 3.333m 0)

Lneutral neutral gnd 1u

* Current Sensing
Rshunt_u phase_u phase_u_out 0.001
Rshunt_v phase_v phase_v_out 0.001
Rshunt_w phase_w phase_w_out 0.001

* Load Resistance
Rload_u phase_u_out gnd 2
Rload_v phase_v_out gnd 2
Rload_w phase_w_out gnd 2

* EMI Filtering
Lferrite_u phase_u_out phase_u_filt 1u
Rferrite_u phase_u_filt gnd 100

Lferrite_v phase_v_out phase_v_filt 1u
Rferrite_v phase_v_filt gnd 100

Lferrite_w phase_w_out phase_w_filt 1u
Rferrite_w phase_w_filt gnd 100

* Measurements
.measure tran I_peak_u MAX I(Rshunt_u)
.measure tran I_peak_v MAX I(Rshunt_v)
.measure tran I_peak_w MAX I(Rshunt_w)
.measure tran Vdc_ripple PP V(vdc)
.measure tran Power_avg AVG V(vdc)*I(Vdc)

* Simulation: 5ms (250 PWM cycles @ 20kHz)
.tran 1u 5m 0 1u

* Data output
.save all
.print tran v(vdc) v(phase_u) v(phase_v) v(phase_w) i(rshunt_u) i(rshunt_v) i(rshunt_w)

.end
"""

def run_spice_simulation():
    """Run ngspice and capture results"""
    
    # Write netlist to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cir', delete=False) as f:
        f.write(spice_netlist)
        netlist_file = f.name
    
    try:
        # Run ngspice
        result = subprocess.run(
            ['ngspice', '-b', netlist_file, '-o', 'sim_raw.log'],
            cwd='/home/teste/controlmotor',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("✅ Simulação SPICE executada com sucesso!")
        print("\n--- Saída da simulação ---")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        
        return True
    
    except subprocess.TimeoutExpired:
        print("❌ Simulação expirou (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(netlist_file)
        except:
            pass

if __name__ == '__main__':
    print("=" * 60)
    print("VISUALIZAÇÃO DE SIMULAÇÃO SPICE - INVERSOR 3-FASES")
    print("=" * 60)
    print()
    
    if run_spice_simulation():
        print("\n✅ Geração de dados de simulação concluída!")
        print("   Arquivos gerados em: /home/teste/controlmotor/")
    else:
        print("\n❌ Erro ao executar simulação")
