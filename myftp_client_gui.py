import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import socket
import os

class MyFTPClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("MyFTP Client")

        self.connection = None

        # Frame de Login
        self.login_frame = tk.Frame(master)
        self.login_frame.pack(pady=10)

        tk.Label(self.login_frame, text="Servidor IP:").grid(row=0, column=0)
        self.server_ip_entry = tk.Entry(self.login_frame)
        self.server_ip_entry.grid(row=0, column=1)
        self.server_ip_entry.insert(0, "127.0.0.1")

        tk.Label(self.login_frame, text="Porta:").grid(row=1, column=0)
        self.port_entry = tk.Entry(self.login_frame)
        self.port_entry.grid(row=1, column=1)
        self.port_entry.insert(0, "2121")

        tk.Label(self.login_frame, text="Usuário:").grid(row=2, column=0)
        self.user_entry = tk.Entry(self.login_frame)
        self.user_entry.grid(row=2, column=1)

        tk.Label(self.login_frame, text="Senha:").grid(row=3, column=0)
        self.pass_entry = tk.Entry(self.login_frame, show="*")
        self.pass_entry.grid(row=3, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Frame principal (comandos) – só será exibido após o login
        self.main_frame = tk.Frame(master)

        self.ls_text = tk.Text(self.main_frame, width=50, height=15)
        self.ls_text.pack(pady=5)

        self.refresh_button = tk.Button(self.main_frame, text="Atualizar Lista (ls)", command=self.ls_command)
        self.refresh_button.pack(pady=5)

        self.put_button = tk.Button(self.main_frame, text="Upload (put)", command=self.put_command)
        self.put_button.pack(pady=5)

        self.get_button = tk.Button(self.main_frame, text="Download (get)", command=self.get_command)
        self.get_button.pack(pady=5)

        self.cd_button = tk.Button(self.main_frame, text="Mudar Diretório (cd)", command=self.cd_command)
        self.cd_button.pack(pady=5)

        self.cd_up_button = tk.Button(self.main_frame, text="Voltar Diretório (cd..)", command=self.cd_up_command)
        self.cd_up_button.pack(pady=5)

        self.mkdir_button = tk.Button(self.main_frame, text="Criar Pasta (mkdir)", command=self.mkdir_command)
        self.mkdir_button.pack(pady=5)

        self.rmdir_button = tk.Button(self.main_frame, text="Remover Pasta (rmdir)", command=self.rmdir_command)
        self.rmdir_button.pack(pady=5)

    def login(self):
        server_ip = self.server_ip_entry.get()
        port = int(self.port_entry.get())
        user = self.user_entry.get()
        pwd = self.pass_entry.get()

        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((server_ip, port))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {str(e)}")
            return

        login_command = f"login {user} {pwd}"
        self.connection.sendall(login_command.encode())
        response = self.connection.recv(1024).decode()
        if "bem-sucedido" in response:
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            self.login_frame.forget()
            self.main_frame.pack()
            self.ls_command()  # Atualiza a listagem de arquivos
        else:
            messagebox.showerror("Login", "Usuário ou senha incorretos.")

    def ls_command(self):
        self.connection.sendall("ls".encode())
        response = self.connection.recv(4096).decode()
        self.ls_text.delete("1.0", tk.END)
        self.ls_text.insert(tk.END, response)

    def put_command(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        filename = os.path.basename(filepath)
        command = f"put {filename}"
        self.connection.sendall(command.encode())
        # Aguarda resposta "READY"
        response = self.connection.recv(1024).decode()
        if response != "READY":
            messagebox.showerror("Erro", f"Servidor respondeu: {response}")
            return
        file_size = os.path.getsize(filepath)
        self.connection.sendall(str(file_size).encode())
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                self.connection.sendall(chunk)
        final_response = self.connection.recv(1024).decode()
        messagebox.showinfo("Upload", final_response)
        self.ls_command()

    def get_command(self):
        filename = simpledialog.askstring("Download", "Digite o nome do arquivo:")
        if not filename:
            return
        command = f"get {filename}"
        self.connection.sendall(command.encode())
        response = self.connection.recv(1024).decode()
        if response.startswith("Erro"):
            messagebox.showerror("Erro", response)
            return
        try:
            file_size = int(response)
        except ValueError:
            messagebox.showerror("Erro", "Tamanho de arquivo inválido.")
            return
        self.connection.sendall("READY".encode())
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if not save_path:
            return
        received_bytes = 0
        with open(save_path, "wb") as f:
            while received_bytes < file_size:
                chunk = self.connection.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
                received_bytes += len(chunk)
        messagebox.showinfo("Download", "Arquivo baixado com sucesso!")
        self.ls_command()

    def cd_command(self):
        folder = simpledialog.askstring("cd", "Digite o nome do diretório:")
        if not folder:
            return
        command = f"cd {folder}"
        self.connection.sendall(command.encode())
        response = self.connection.recv(1024).decode()
        messagebox.showinfo("cd", response)
        self.ls_command()

    def cd_up_command(self):
        command = "cd.."
        self.connection.sendall(command.encode())
        response = self.connection.recv(1024).decode()
        messagebox.showinfo("cd..", response)
        self.ls_command()

    def mkdir_command(self):
        folder = simpledialog.askstring("mkdir", "Digite o nome da nova pasta:")
        if not folder:
            return
        command = f"mkdir {folder}"
        self.connection.sendall(command.encode())
        response = self.connection.recv(1024).decode()
        messagebox.showinfo("mkdir", response)
        self.ls_command()

    def rmdir_command(self):
        folder = simpledialog.askstring("rmdir", "Digite o nome da pasta a ser removida:")
        if not folder:
            return
        command = f"rmdir {folder}"
        self.connection.sendall(command.encode())
        response = self.connection.recv(1024).decode()
        messagebox.showinfo("rmdir", response)
        self.ls_command()

if __name__ == "__main__":
    root = tk.Tk()
    app = MyFTPClientGUI(root)
    root.mainloop()