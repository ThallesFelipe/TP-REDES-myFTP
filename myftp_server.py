import socket
import threading
import os

# Usuários pré-cadastrados: login: senha
users = {
    "usuario1": "senha1",
    "usuario2": "senha2",
    "thalles": "1234",
    "thais": "1234",
    "admin": "admin"
}

# Diretório base para as operações do servidor (garante que os clientes não saiam dessa raiz)
BASE_DIR = os.path.abspath("server_files")
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)

def client_handler(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    current_dir = BASE_DIR  # Cada cliente terá seu próprio diretório atual
    authenticated = False

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            command = data.strip()
            print(f"Recebido de {addr}: {command}")

            # Comando de login
            if command.startswith("login"):
                # Sintaxe: login <usuario> <senha>
                parts = command.split()
                if len(parts) != 3:
                    conn.sendall("Erro: Comando login inválido. Use: login <usuario> <senha>\n".encode())
                    continue
                _, username, password = parts
                if username in users and users[username] == password:
                    authenticated = True
                    conn.sendall("Login bem-sucedido!\n".encode())
                else:
                    conn.sendall("Erro: Usuário ou senha incorretos.\n".encode())

            # Se não estiver autenticado, só permite login
            elif not authenticated:
                conn.sendall("Erro: Você deve fazer login primeiro.\n".encode())

            # Comando put: envia um arquivo do cliente para o servidor
            elif command.startswith("put"):
                # Sintaxe: put <nome_arquivo>
                parts = command.split()
                if len(parts) != 2:
                    conn.sendall("Erro: Comando put inválido. Use: put <nome_arquivo>\n".encode())
                    continue
                filename = parts[1]
                file_path = os.path.join(current_dir, filename)
                # Informa ao cliente que está pronto para receber o arquivo
                conn.sendall("READY".encode())
                # Recebe o tamanho do arquivo
                file_size_str = conn.recv(1024).decode()
                try:
                    file_size = int(file_size_str)
                except ValueError:
                    conn.sendall("Erro: Tamanho de arquivo inválido.\n".encode())
                    continue
                received_bytes = 0
                with open(file_path, "wb") as f:
                    while received_bytes < file_size:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_bytes += len(chunk)
                conn.sendall("Arquivo recebido com sucesso.\n".encode())

            # Comando get: envia um arquivo do servidor para o cliente
            elif command.startswith("get"):
                # Sintaxe: get <nome_arquivo>
                parts = command.split()
                if len(parts) != 2:
                    conn.sendall("Erro: Comando get inválido. Use: get <nome_arquivo>\n".encode())
                    continue
                filename = parts[1]
                file_path = os.path.join(current_dir, filename)
                if not os.path.exists(file_path):
                    conn.sendall("Erro: Arquivo não encontrado.\n".encode())
                    continue
                file_size = os.path.getsize(file_path)
                # Envia o tamanho do arquivo para o cliente
                conn.sendall(str(file_size).encode())
                # Aguarda confirmação do cliente
                ack = conn.recv(1024).decode()
                if ack != "READY":
                    continue
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        conn.sendall(chunk)

            # Comando ls: lista os arquivos e pastas no diretório atual
            elif command.startswith("ls"):
                try:
                    items = os.listdir(current_dir)
                    response = "\n".join(items) if items else "Diretório vazio."
                    conn.sendall(response.encode())
                except Exception as e:
                    conn.sendall(f"Erro ao listar diretório: {str(e)}".encode())

            # Comando cd: muda para um diretório especificado
            elif command.startswith("cd "):
                parts = command.split(maxsplit=1)
                if len(parts) != 2:
                    conn.sendall("Erro: Comando cd inválido. Use: cd <nome_da_pasta>\n".encode())
                    continue
                folder = parts[1]
                new_path = os.path.join(current_dir, folder)
                if os.path.exists(new_path) and os.path.isdir(new_path):
                    current_dir = os.path.abspath(new_path)
                    # Garante que não saia do BASE_DIR
                    if not current_dir.startswith(BASE_DIR):
                        current_dir = BASE_DIR
                        conn.sendall("Acesso negado a diretórios acima da raiz.\n".encode())
                    else:
                        conn.sendall(f"Diretório alterado para {current_dir}\n".encode())
                else:
                    conn.sendall("Erro: Diretório não encontrado.\n".encode())

            # Comando cd..: volta para o diretório anterior
            elif command.strip() == "cd..":
                parent = os.path.dirname(current_dir)
                if parent.startswith(BASE_DIR):
                    current_dir = parent
                    conn.sendall(f"Diretório alterado para {current_dir}\n".encode())
                else:
                    conn.sendall("Erro: Já está no diretório raiz.\n".encode())

            # Comando mkdir: cria um novo diretório
            elif command.startswith("mkdir"):
                parts = command.split()
                if len(parts) != 2:
                    conn.sendall("Erro: Comando mkdir inválido. Use: mkdir <nome_da_pasta>\n".encode())
                    continue
                folder = parts[1]
                new_dir = os.path.join(current_dir, folder)
                try:
                    os.mkdir(new_dir)
                    conn.sendall("Diretório criado com sucesso.\n".encode())
                except Exception as e:
                    conn.sendall(f"Erro ao criar diretório: {str(e)}\n".encode())

            # Comando rmdir: remove um diretório
            elif command.startswith("rmdir"):
                parts = command.split()
                if len(parts) != 2:
                    conn.sendall("Erro: Comando rmdir inválido. Use: rmdir <nome_da_pasta>\n".encode())
                    continue
                folder = parts[1]
                dir_path = os.path.join(current_dir, folder)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        conn.sendall("Diretório removido com sucesso.\n".encode())
                    except Exception as e:
                        conn.sendall(f"Erro ao remover diretório: {str(e)}\n".encode())
                else:
                    conn.sendall("Erro: Diretório não encontrado.\n".encode())

            else:
                conn.sendall("Comando não reconhecido.\n".encode())
        except Exception as e:
            print(f"Erro com {addr}: {str(e)}")
            break

    conn.close()
    print(f"Conexão encerrada com {addr}")

def start_server(host="0.0.0.0", port=2121):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor MyFTP rodando em {host}:{port}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.daemon = True  # encerra a thread caso o main seja finalizado
        thread.start()

if __name__ == "__main__":
    start_server()