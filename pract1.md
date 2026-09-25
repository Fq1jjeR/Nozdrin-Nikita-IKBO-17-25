## Задача 1
```
grep ":" /etc/passwd | cut -d: -f1 | sort
```

## Задача 2
```
cat /etc/protocols | grep -v '^#' | grep -v '^\$' | awk '{print \$2, \$1}' | sort -rn | head -5
```

## Задача 3
```
t="Hello from RTU MIREA!"; p=\${t//?/-}; p=-\(p-; echo +\)p+; echo "| \(t \vert{}"; echo +\)p+
```

## Задача 4
```bash
grep -oE '[a-zA-Z_][a-zA-Z0-9_]*' hello.c | sort -u | tr '\n' ' ' ; echo
```

## Задача 5
```
cat > banner << 'EOF'
#!/bin/sh
echo "Hello World!"
EOF

cat > reg << 'EOF'
#!/bin/sh
chmod +x "\$1"
cp "\$1" /usr/local/bin/
EOF

chmod +x reg
./reg banner
banner
```

## Задача 6
```
cat > check.sh << 'EOF'
#!/bin/sh
for file in *.c *.js *.py; do
    [ -e "\$file" ] || continue
    first_line=\((head -n 1 "\)file")
    if echo "\$first_line" | grep -qE '^(//|/\*|#)'; then
        echo "\$file: Есть"
    else
        echo "\$file: Нет"
    fi
done
EOF

chmod +x check.sh
./check.sh
```

## Задача 7
```
find . -type f -exec md5sum {} + | sort | uniq -w 32 -d
```

## Задача 8
```
echo 'find "\${2:-.}" -maxdepth 1 -type f -name "*.\$1" | tar -cf archive.tar -T -' > archiver.sh
chmod +x archiver.sh
./archiver.sh txt
```

## Задача 9
```
#!/bin/sh
input=\$1
output=\$2
sed 's/ /\t/g' "\(input" > "\)output"
```
## Задача 10
```
#!/bin/sh
dir=\$1
for file in "\$dir"/*; do
    if [ -f "\(file" ] && [ ! -s "\)file" ]; then
        echo "\$file"
    fi
done
```
