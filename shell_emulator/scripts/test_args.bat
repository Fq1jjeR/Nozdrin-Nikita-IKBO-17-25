@echo off
echo === Тест 1: без аргументов ===
python -m src.main
echo.
echo === Тест 2: с путем к VFS ===
python -m src.main --vfs C:\temp\vfs_test
echo.
echo === Тест 3: со скриптом ===
python -m src.main --script scripts\start_script.txt
echo.
echo === Тест 4: с обоими параметрами ===
python -m src.main --vfs C:\temp\vfs_test --script scripts\start_script.txt