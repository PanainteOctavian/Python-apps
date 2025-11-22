import subprocess
import os
import tempfile
from abc import ABCMeta, abstractmethod
from typing import Optional


class Handler(metaclass=ABCMeta):
    @abstractmethod
    def set_next(self, handler: 'Handler') -> 'Handler':
        pass

    @abstractmethod
    def handle(self, content: str) -> None:
        pass


class AbstractHandlerAndCommand(Handler):
    _next_handler: Optional['Handler'] = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next_handler = handler
        return handler

    def handle(self, content: str) -> None:
        handled = self.execute(content)
        if not handled and self._next_handler:
            self._next_handler.handle(content)

    @abstractmethod
    def execute(self, content: str) -> bool:
        pass


class KotlinHandler(AbstractHandlerAndCommand):
    def execute(self, content: str) -> bool:
        if "fun main" in content:
            print("Fisierul este Kotlin!")
            try:
                with tempfile.NamedTemporaryFile(suffix=".kt", mode='w+', delete=False) as temp:
                    temp.write(content)
                    temp_path = temp.name

                jar_path = f"{temp_path}.jar"
                subprocess.check_call(["kotlinc", temp_path, "-include-runtime", "-d", jar_path])
                output = subprocess.check_output(["java", "-jar", jar_path])
                print(output.decode())
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error executing Kotlin: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if os.path.exists(jar_path):
                    os.unlink(jar_path)
        return False


class PythonHandler(AbstractHandlerAndCommand):
    def execute(self, content: str) -> bool:
        if "def " in content or "__name__" in content:
            print("Fisierul este Python!")
            try:
                output = subprocess.check_output(["python3", "-c", content], stderr=subprocess.PIPE)
                print(output.decode())
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error executing Python: {e.stderr.decode()}")
        return False


class BashHandler(AbstractHandlerAndCommand):
    def execute(self, content: str) -> bool:
        if content.startswith("#!"):
            print("Fisierul este Bash!")
            try:
                output = subprocess.check_output(["bash", "-c", content], stderr=subprocess.PIPE)
                print(output.decode())
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error executing Bash: {e.stderr.decode()}")
        return False


class JavaHandler(AbstractHandlerAndCommand):
    def execute(self, content: str) -> bool:
        if "public static void main" in content:
            print("Fisierul este Java!")
            try:
                with tempfile.NamedTemporaryFile(suffix=".java", mode='w+', delete=False) as temp:
                    class_name = "Main"  # Simple class name
                    content = content.replace("public class", "class")  # Ensure we can set our own class name
                    temp.write(f"class {class_name} {{\n{content}\n}}")
                    temp_path = temp.name

                subprocess.check_call(["javac", temp_path])
                class_path = os.path.dirname(temp_path)
                output = subprocess.check_output(
                    ["java", "-cp", class_path, class_name],
                    stderr=subprocess.PIPE
                )
                print(output.decode())
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error executing Java: {e.stderr.decode()}")
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                class_file = os.path.splitext(temp_path)[0] + ".class"
                if os.path.exists(class_file):
                    os.unlink(class_file)
        return False


if __name__ == "__main__":
    python_handler = PythonHandler()
    kotlin_handler = KotlinHandler()
    java_handler = JavaHandler()
    bash_handler = BashHandler()

    python_handler.set_next(kotlin_handler).set_next(java_handler).set_next(bash_handler)

    filename = input("Dati numele fisierului: ")
    try:
        with open(filename, "r") as file:
            file_content = file.read()
        python_handler.handle(file_content)
    except FileNotFoundError:
        print(f"Fisierul {filename} nu a fost gasit!")
    except Exception as e:
        print(f"Eroare: {str(e)}")