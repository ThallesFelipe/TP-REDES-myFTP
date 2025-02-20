## Como Executar

### 1. Servidor
1. **Preparação:**  
   - Certifique-se de que o diretório `ftp_files` exista no mesmo local do `myftp_server.py` (o código criará o diretório automaticamente, se necessário).
2. **Iniciar o Servidor:**  
   - Abra o terminal, navegue até o diretório do projeto e execute:
     ```bash
     python myftp_server.py
     ```
   - O servidor ficará rodando e aguardando conexões na porta **2121**.

### 2. Cliente de Linha de Comando
1. **Iniciar o Cliente CLI:**  
   - No terminal, navegue até o diretório do projeto e execute:
     ```bash
     python myftp_client.py
     ```
2. **Realize o Login:**  
   - Digite o IP do servidor (por exemplo, `127.0.0.1` para teste local) e, em seguida, utilize o comando:
     ```
     login user1 password1
     ```
3. **Utilize os Comandos:**  
   - **put:** `put nome_arquivo` para enviar um arquivo.
   - **get:** `get nome_arquivo` para baixar um arquivo.
   - **ls:** para listar os arquivos/diretórios.
   - **cd:** para mudar de diretório.
   - **cd..:** para voltar para o diretório anterior.
   - **mkdir:** para criar um novo diretório.
   - **rmdir:** para remover um diretório.

### 3. Cliente com Interface Gráfica
1. **Iniciar o Cliente GUI:**  
   - No terminal, execute:
     ```bash
     python myftp_client_gui.py
     ```
2. **Login e Uso:**  
   - Preencha o formulário com o IP do servidor, usuário e senha (por exemplo, `127.0.0.1`, `user1`, `password1`).
   - Após o login, utilize os botões para enviar/receber arquivos e gerenciar diretórios.

---

## Como Testar

1. **Teste de Conexão:**
   - Execute o servidor e, em seguida, conecte um ou mais clientes (CLI ou GUI) simultaneamente para testar a multi-threading.
2. **Teste de Autenticação:**
   - Utilize credenciais válidas (por exemplo, `user1` e `password1`) e inválidas para verificar o tratamento de login.
3. **Teste de Transferência de Arquivos:**
   - Envie arquivos de diferentes tamanhos e formatos com o comando `put` e recupere-os com `get`.
4. **Teste de Gerenciamento de Diretórios:**
   - Execute os comandos `ls`, `cd`, `cd..`, `mkdir` e `rmdir` e verifique as respostas do servidor.
5. **Tratamento de Erros:**
   - Tente acessar diretórios ou arquivos inexistentes para confirmar que as mensagens de erro são exibidas corretamente.

---

## Licença

Este projeto é fornecido "como está", sem garantias explícitas de qualquer tipo. Sinta-se à vontade para modificar e melhorar o código conforme necessário para seus estudos ou projetos.

---

## Conclusão

MyFTP é um projeto educacional que demonstra conceitos de redes, programação concorrente com threads e desenvolvimento de interfaces gráficas em Python. Ele serve como base para explorar e expandir funcionalidades em sistemas de transferência de arquivos.
