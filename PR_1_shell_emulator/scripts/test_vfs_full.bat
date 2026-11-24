@echo off
echo === Создание полной VFS (3 уровня) ===
if not exist C:\temp\vfs_full\dir1\subdir1 mkdir C:\temp\vfs_full\dir1\subdir1
if not exist C:\temp\vfs_full\dir2 mkdir C:\temp\vfs_full\dir2
echo content1 > C:\temp\vfs_full\file1.txt
echo content2 > C:\temp\vfs_full\dir1\file2.txt
echo content3 > C:\temp\vfs_full\dir1\subdir1\file3.txt
echo === Запуск эмулятора ===
python -m src.main --vfs C:\temp\vfs_full --script scripts\start_script.txt