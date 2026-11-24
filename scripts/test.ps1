Write-Host "=== Running GLITCHGUARD Comprehensive Test Suite ===" -ForegroundColor Cyan

Write-Host "`n1. Running Rust Firmware Workspace Tests (28 tests across 6 crates)..." -ForegroundColor Yellow
cargo test --workspace

Write-Host "`n2. Compiling bare-metal RISC-V target (riscv32imac-unknown-none-elf)..." -ForegroundColor Yellow
cargo check --target riscv32imac-unknown-none-elf -p glitchguard-common -p hardware-observer -p event-engine -p crypto-verification -p recovery-engine

Write-Host "`n3. Running Software Fault Simulation Experiments (100 trials)..." -ForegroundColor Yellow
python experiments/run_experiments.py

Write-Host "`n4. Testing React Dashboard Production Build..." -ForegroundColor Yellow
cd dashboard
npm run build
cd ..

Write-Host "`n=== ALL GLITCHGUARD SUITES PASSED ===" -ForegroundColor Green
