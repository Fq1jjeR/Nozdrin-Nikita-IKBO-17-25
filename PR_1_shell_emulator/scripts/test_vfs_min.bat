@echo off
echo === Создание минимальной VFS ===
if not exist C:\temp\vfs_min mkdir C:\temp\vfs_min
echo hello > C:\temp\vfs_min\file.txt
echo === Запуск эмулятора ===
python -m src.main --vfs C:\temp\vfs_min