import subprocess
from typing import List, Union

if __name__ == "__main__":
    command: str = input("Dati comanda : ")
    commands: List[str] = command.split("|")
    process: List[subprocess.Popen] = []

    for i, command in enumerate(commands):
        if i == 0:
            process.append(subprocess.Popen(command.strip().split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        else:
            process.append(subprocess.Popen(command.strip().split(), stdin=process[i - 1].stdout, stdout=subprocess.PIPE))

    output: Union[str, bytes] = process[-1].communicate()[0]

    print(f"Iesirea : {output.decode()}")
