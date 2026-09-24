## Задача 1:

grep ":" /etc/passwd | cut -d: -f1 | sort

## Задача 2

cat /etc/protocols | grep -v '^#' | grep -v '^$' | awk '{print $2, $1}' | sort -rn | head -5

## Задача 3

t="Hello from RTU MIREA!"; p=${t//?/-}; p=-$p-; echo +$p+; echo "| $t |"; echo +$p+

## Задача 4

grep -oE '[a-zA-Z_][a-zA-Z0-9_]*' hello.c | sort -u | tr '\n' ' ' ; echo

## Задача 5



## Задача 6



## Задача 7



## Задача 8



## Задача 9



## Задача 10


