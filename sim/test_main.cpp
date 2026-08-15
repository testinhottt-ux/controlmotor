#include "motor_model.h"
#include "controller_core.h"
#include <iostream>
#include <iomanip>
#include <cmath>

using namespace std;

/**
 * BLOCO 1: TESTE NATIVO — Motor Simulado + Controlador
 * 
 * Valida:
 * 1. Motor gira e converge ao alvo (Teste A)
 * 2. Auto-learning produz ganhos estáveis (Teste B)
 * 3. Alteração de parâmetros por software funciona (Teste C)
 */

bool test_A_motor_convergence() {
    cout << "\n=== TESTE A: Motor Gira e Converge ===" << endl;
    cout << "Objetivo: RPM alvo = 3000; deve convergir a ±5% em <2s (critério realista)" << endl;
    cout << "---" << endl;
    
    // Ganhos otimizados pelo auto-learning (use valores típicos de produção)
    MotorModel motor;
    PIController controller(0.3, 0.03, 0.01);  // Ganhos conservadores produção
    
    double rpm_target = 3000.0;
    int max_steps = 20000;  // 2 segundos @ 10 kHz
    double rpm_at_100ms = 0, rpm_at_500ms = 0, rpm_at_1s = 0;
    
    for (int step = 0; step < max_steps; step++) {
        // Controlador PI
        double i_cmd = controller.compute(rpm_target, motor.getRPM(), 1e-4);
        
        // Motor simula dinâmica
        motor.step(i_cmd);
        
        // Log em pontos de interesse
        if (step == 1000) rpm_at_100ms = motor.getRPM();
        if (step == 5000) rpm_at_500ms = motor.getRPM();
        if (step == 10000) rpm_at_1s = motor.getRPM();
    }
    
    double rpm_final = motor.getRPM();
    double error_percent = std::abs(rpm_final - rpm_target) / rpm_target * 100.0;
    
    cout << fixed << setprecision(1);
    cout << "t=100ms:   RPM = " << rpm_at_100ms << endl;
    cout << "t=500ms:   RPM = " << rpm_at_500ms << endl;
    cout << "t=1.0s:    RPM = " << rpm_at_1s << endl;
    cout << "t=2.0s:    RPM = " << rpm_final << endl;
    cout << "Erro final: " << error_percent << "% (alvo: <5%)" << endl;
    
    bool pass = error_percent < 5.0;  // Critério realista para sim. sem carga
    cout << (pass ? "✓ PASS" : "✗ FAIL") << endl;
    return pass;
}

bool test_B_autolearning() {
    cout << "\n=== TESTE B: Auto-Learning Converge ===" << endl;
    cout << "Objetivo: Rodar relay auto-tune; produzir Kp/Ki/Kd finitos e estáveis" << endl;
    cout << "---" << endl;
    
    MotorModel motor;
    RelayAutoTuner tuner(3000.0);
    
    // Fase 1: Relay perturbation (duração: ~20 segundos de simulação)
    tuner.start();
    int max_steps = 200000;  // 20 segundos
    
    for (int step = 0; step < max_steps; step++) {
        // Relay oscila ao redor do setpoint
        double i_cmd = tuner.relayStep(motor.getRPM());
        motor.step(i_cmd);
        tuner.updateOscillation(motor.getRPM());
        
        if (tuner.isDone()) break;
    }
    
    double Kp, Ki, Kd;
    tuner.getResults(Kp, Ki, Kd);
    
    cout << fixed << setprecision(4);
    cout << "Kp resultado = " << Kp << " (range: [" << ParamStore::KP_MIN << ".." << ParamStore::KP_MAX << "])" << endl;
    cout << "Ki resultado = " << Ki << " (range: [" << ParamStore::KI_MIN << ".." << ParamStore::KI_MAX << "])" << endl;
    cout << "Kd resultado = " << Kd << " (range: [" << ParamStore::KD_MIN << ".." << ParamStore::KD_MAX << "])" << endl;
    cout << "Oscilações detectadas: " << tuner.zero_crossings << endl;
    
    // Verificar se os ganhos são válidos
    bool kp_valid = (Kp >= ParamStore::KP_MIN && Kp <= ParamStore::KP_MAX);
    bool ki_valid = (Ki >= ParamStore::KI_MIN && Ki <= ParamStore::KI_MAX);
    bool kd_valid = (Kd >= ParamStore::KD_MIN && Kd <= ParamStore::KD_MAX);
    bool all_positive = (Kp > 0 && Ki > 0 && Kd > 0);
    
    bool pass = kp_valid && ki_valid && kd_valid && all_positive;
    cout << (pass ? "✓ PASS" : "✗ FAIL") << " — Ganhos válidos e positivos" << endl;
    
    return pass;
}

bool test_C_param_software() {
    cout << "\n=== TESTE C: Alteração de Parâmetros por Software ===" << endl;
    cout << "Objetivo: setKp/Ki/Kd devem aplicar valor com clamp automático" << endl;
    cout << "---" << endl;
    
    ParamStore params;
    int passes = 0;
    
    // Caso 1: Valor dentro dos limites
    cout << "Caso 1: setKp(1.2) — dentro dos limites" << endl;
    params.setKp(1.2);
    if (params.getKp() == 1.2) {
        cout << "  ✓ Kp = " << fixed << setprecision(2) << params.getKp() << endl;
        passes++;
    } else {
        cout << "  ✗ Falhou: esperado 1.2, obteve " << params.getKp() << endl;
    }
    
    // Caso 2: Valor acima do máximo (deve clampar)
    cout << "Caso 2: setKp(999) — acima do máximo, deve clampar a " << ParamStore::KP_MAX << endl;
    params.setKp(999.0);
    if (params.getKp() == ParamStore::KP_MAX) {
        cout << "  ✓ Kp clamped a " << fixed << setprecision(2) << params.getKp() << endl;
        passes++;
    } else {
        cout << "  ✗ Falhou: esperado " << ParamStore::KP_MAX << ", obteve " << params.getKp() << endl;
    }
    
    // Caso 3: Valor abaixo do mínimo (deve clampar)
    cout << "Caso 3: setKp(-1) — abaixo do mínimo, deve clampar a " << ParamStore::KP_MIN << endl;
    params.setKp(-1.0);
    if (params.getKp() == ParamStore::KP_MIN) {
        cout << "  ✓ Kp clamped a " << fixed << setprecision(4) << params.getKp() << endl;
        passes++;
    } else {
        cout << "  ✗ Falhou: esperado " << ParamStore::KP_MIN << ", obteve " << params.getKp() << endl;
    }
    
    // Teste Ki e Kd similares
    cout << "Caso 4: setKi(0.5) — dentro limites" << endl;
    params.setKi(0.5);
    if (params.getKi() == 0.5) {
        cout << "  ✓ Ki = " << fixed << setprecision(2) << params.getKi() << endl;
        passes++;
    } else {
        cout << "  ✗ Falhou" << endl;
    }
    
    cout << "Caso 5: setKd(0.1) — dentro limites" << endl;
    params.setKd(0.1);
    if (params.getKd() == 0.1) {
        cout << "  ✓ Kd = " << fixed << setprecision(2) << params.getKd() << endl;
        passes++;
    } else {
        cout << "  ✗ Falhou" << endl;
    }
    
    bool pass = (passes == 5);
    cout << (pass ? "✓ PASS" : "✗ FAIL") << " — " << passes << "/5 casos OK" << endl;
    return pass;
}

int main() {
    cout << "\n" << string(60, '=') << endl;
    cout << "BLOCO 1: TESTE NATIVO VERIFICÁVEL" << endl;
    cout << "Motor Simulado + Controlador PI + Auto-Learning" << endl;
    cout << string(60, '=') << endl;
    
    bool test_a_pass = test_A_motor_convergence();
    bool test_b_pass = test_B_autolearning();
    bool test_c_pass = test_C_param_software();
    
    cout << "\n" << string(60, '=') << endl;
    cout << "RESUMO FINAL" << endl;
    cout << string(60, '=') << endl;
    cout << "Teste A (motor converge): " << (test_a_pass ? "✓ PASS" : "✗ FAIL") << endl;
    cout << "Teste B (auto-learning):  " << (test_b_pass ? "✓ PASS" : "✗ FAIL") << endl;
    cout << "Teste C (param software): " << (test_c_pass ? "✓ PASS" : "✗ FAIL") << endl;
    cout << string(60, '=') << endl;
    
    int exit_code = (test_a_pass && test_b_pass && test_c_pass) ? 0 : 1;
    cout << "\nExit code: " << exit_code << endl;
    
    return exit_code;
}
